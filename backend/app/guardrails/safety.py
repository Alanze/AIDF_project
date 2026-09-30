from dataclasses import dataclass
import re


CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")
TRADITIONAL_HINT_RE = re.compile(r"[萬與專業險靈選擇額價值後會費風險應該買]")

INSURANCE_SCOPE_TERMS = {
    "premium",
    "cash",
    "policy",
    "insurance",
    "insured",
    "benefit",
    "withdrawal",
    "surrender",
    "interest",
    "bonus",
    "death",
    "terminal",
    "unemployment",
    "charge",
    "fee",
    "guaranteed",
    "flexi",
    "ulife",
    "保费",
    "保費",
    "现金",
    "現金",
    "保单",
    "保單",
    "保险",
    "保險",
    "保障",
    "提款",
    "退保",
    "利息",
    "回报",
    "回報",
    "身故",
    "失业",
    "失業",
    "费用",
    "費用",
}

PERSONAL_ADVICE_TERMS = {
    "should i buy",
    "should i cancel",
    "should i surrender",
    "recommend",
    "best for me",
    "suitable for me",
    "我该买",
    "我該買",
    "适合我",
    "適合我",
    "应不应该",
    "應不應該",
    "要不要买",
    "要不要買",
}


@dataclass(frozen=True)
class QuestionAssessment:
    language: str
    scope_status: str
    message: str
    not_enough_context_message: str
    personal_advice_warning: str | None


def detect_language(text: str) -> str:
    if CHINESE_RE.search(text):
        if TRADITIONAL_HINT_RE.search(text):
            return "zh-Hant"
        return "zh-Hans"
    return "en"


def _contains_any(text: str, terms: set[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered or term in text for term in terms)


def assess_question(question: str) -> QuestionAssessment:
    language = detect_language(question)
    in_scope = _contains_any(question, INSURANCE_SCOPE_TERMS)
    asks_personal_advice = _contains_any(question, PERSONAL_ADVICE_TERMS)

    if language.startswith("zh"):
        out_of_scope_message = "这个问题超出了当前保险产品资料的范围。我可以解释 FLEXI-ULife Prime Saver 的保障、费用、风险、提款、缴费和除外责任等内容。"
        no_context_message = "我在提供的产品资料中没有找到足够依据回答这个问题。请参考正式保单文件，或咨询合资格的保险顾问。"
        warning = "我可以解释资料中的条款，但不能判断你是否应该购买、退保或选择某个保险方案。"
    else:
        out_of_scope_message = "This question is outside the scope of the supplied insurance product document. I can explain FLEXI-ULife Prime Saver benefits, fees, risks, withdrawals, premiums, and exclusions."
        no_context_message = "I could not find enough evidence in the supplied product document to answer this. Please refer to the formal policy document or consult a qualified insurance professional."
        warning = "I can explain the document terms, but I cannot advise whether you should buy, surrender, or choose a specific insurance plan."

    return QuestionAssessment(
        language=language,
        scope_status="in_scope" if in_scope or asks_personal_advice else "out_of_scope",
        message=out_of_scope_message,
        not_enough_context_message=no_context_message,
        personal_advice_warning=warning if asks_personal_advice else None,
    )
