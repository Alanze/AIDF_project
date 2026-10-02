import re

from app.case_understanding.schemas import UserCase


AGE_PATTERNS = [
    re.compile(r"(?P<age>\d{1,3})\s*(?:岁|歲)"),
    re.compile(r"(?:age|aged)\s*(?P<age>\d{1,3})", re.IGNORECASE),
]

POLICY_YEAR_PATTERNS = [
    re.compile(r"(?:买了|買了|投保|持有|供了|缴了|繳了)\s*(?P<years>\d{1,2})\s*(?:年|yrs?|years?)", re.IGNORECASE),
    re.compile(r"(?:买了|買了|持有|已有|已经买|已經買).{0,12}?(?P<years>\d{1,2})\s*(?:年|yrs?|years?)", re.IGNORECASE),
    re.compile(r"(?P<years>\d{1,2})\s*(?:年|yrs?|years?)\s*(?:保单|保單|policy)", re.IGNORECASE),
]

ACTION_TERMS = {
    "skip_premium": ["暂停缴费", "暫停繳費", "暂停缴付保费", "暫停繳付保費", "暂停投保", "暫停投保", "停缴", "停繳", "skip premium"],
    "withdraw_cash": ["提款", "提取现金", "提取現金", "withdraw", "cash withdrawal"],
    "surrender": ["退保", "surrender", "terminate policy", "cancel policy"],
    "switch_plan": ["改用其他方案", "换方案", "換方案", "转换方案", "轉換方案", "switch plan", "change plan"],
    "buy": ["购买", "購買", "准备投保", "打算投保", "buy", "purchase"],
    "claim": ["索赔", "索償", "claim"],
}

ADVICE_TERMS = [
    "应不应该",
    "應不應該",
    "该不该",
    "該不該",
    "要不要",
    "适合我",
    "適合我",
    "建议我",
    "建議我",
    "建议",
    "建議",
    "给我一些建议",
    "給我一些建議",
    "有什么建议",
    "有什麼建議",
    "should i",
    "recommend",
    "advice",
    "suitable for me",
]


def extract_user_case(question: str) -> UserCase:
    facts: list[str] = []
    missing_info: list[str] = []
    lowered = question.lower()

    age = _extract_first_int(question, AGE_PATTERNS)
    if age is not None and 0 <= age <= 120:
        facts.append(f"age={age}")
    else:
        age = None

    policy_years = _extract_first_int(question, POLICY_YEAR_PATTERNS)
    if policy_years is not None:
        facts.append(f"policy_years={policy_years}")

    has_existing_policy = _detect_existing_policy(question, lowered)
    if has_existing_policy is not None:
        facts.append(f"has_existing_policy={has_existing_policy}")

    action_considered = _detect_action(question, lowered)
    if action_considered:
        facts.append(f"action_considered={action_considered}")

    cash_value_known = _detect_cash_value_known(question, lowered)
    if cash_value_known is not None:
        facts.append(f"cash_value_known={cash_value_known}")

    premium_status = _detect_premium_status(question, lowered)
    if premium_status:
        facts.append(f"premium_status={premium_status}")

    region = _detect_region(question, lowered)
    if region:
        facts.append(f"region={region}")

    asks_personal_advice = any(term in lowered or term in question for term in ADVICE_TERMS)
    if asks_personal_advice:
        facts.append("asks_personal_advice=True")

    has_case_context = bool(facts)
    if has_case_context:
        missing_info = _missing_information(action_considered, cash_value_known, premium_status)

    return UserCase(
        has_case_context=has_case_context,
        age=age,
        has_existing_policy=has_existing_policy,
        policy_years=policy_years,
        action_considered=action_considered,
        cash_value_known=cash_value_known,
        premium_status=premium_status,
        region=region,
        asks_personal_advice=asks_personal_advice,
        extracted_facts=facts,
        missing_info=missing_info,
    )


def _extract_first_int(text: str, patterns: list[re.Pattern[str]]) -> int | None:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return int(match.groupdict().get("age") or match.groupdict().get("years"))
    return None


def _detect_existing_policy(question: str, lowered: str) -> bool | None:
    if any(term in question for term in ["已经买", "已經買", "买了", "買了", "持有", "已有", "已经投保", "已經投保"]):
        return True
    if any(term in lowered for term in ["existing policy", "already bought", "already have", "i have a policy"]):
        return True
    if any(term in question for term in ["还没买", "還沒買", "没有买", "沒有買", "未投保"]):
        return False
    if any(term in lowered for term in ["do not have a policy", "haven't bought", "not bought"]):
        return False
    return None


def _detect_action(question: str, lowered: str) -> str | None:
    for action, terms in ACTION_TERMS.items():
        if any(term in lowered or term in question for term in terms):
            return action
    return None


def _detect_cash_value_known(question: str, lowered: str) -> bool | None:
    if any(term in question for term in ["现金价值", "現金價值"]) or "cash value" in lowered:
        if any(term in question for term in ["不知道", "不清楚", "未知"]) or any(term in lowered for term in ["unknown", "not sure"]):
            return False
        return True
    return None


def _detect_premium_status(question: str, lowered: str) -> str | None:
    if any(term in question for term in ["收入不稳定", "收入不穩定", "交不起", "缴不起", "繳不起"]):
        return "premium_pressure"
    if any(term in question for term in ["逾期", "宽限期", "寬限期"]) or any(term in lowered for term in ["overdue", "grace period"]):
        return "overdue_or_grace_period"
    if any(term in question for term in ["正常缴费", "正常繳費"]) or "paying normally" in lowered:
        return "paying_normally"
    return None


def _detect_region(question: str, lowered: str) -> str | None:
    if "香港" in question or "hong kong" in lowered:
        return "Hong Kong"
    if "澳门" in question or "澳門" in question or "macau" in lowered:
        return "Macau"
    return None


def _missing_information(action: str | None, cash_value_known: bool | None, premium_status: str | None) -> list[str]:
    missing: list[str] = []
    if action in {"skip_premium", "withdraw_cash", "surrender"}:
        if cash_value_known is not True:
            missing.append("current_cash_value")
        if premium_status is None:
            missing.append("premium_status")
        missing.append("monthly_charges")
        missing.append("formal_policy_terms")
    elif action == "switch_plan":
        missing.extend(["current_cash_value", "monthly_charges", "alternative_plan_terms", "formal_policy_terms"])
    elif action == "buy":
        missing.extend(["financial_goals", "risk_tolerance", "formal_advice"])
    return missing
