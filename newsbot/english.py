from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Vocab:
    word: str
    phonetic: str
    meaning: str
    example: str
    example_zh: str


@dataclass(frozen=True)
class Lesson:
    day: int
    theme: str
    theme_zh: str
    focus: str
    focus_zh: str
    words: tuple[Vocab, ...]
    practice_en: str
    practice_zh: str
    tip: str


# 28-day rotating plan (about 15–20 minutes/day). Day is 1-indexed.
LESSONS: tuple[Lesson, ...] = (
    Lesson(
        1,
        "Daily routines",
        "日常生活",
        "Present simple for habits",
        "用一般现在时描述习惯",
        (
            Vocab("routine", "/ruːˈtiːn/", "日常安排", "I follow a morning routine.", "我有固定的早晨安排。"),
            Vocab("commute", "/kəˈmjuːt/", "通勤", "My commute takes 40 minutes.", "我通勤要四十分钟。"),
            Vocab("priority", "/praɪˈɒrəti/", "优先事项", "Sleep is my top priority.", "睡眠是我的首要事项。"),
            Vocab("deadline", "/ˈdedlaɪn/", "截止日期", "I finished it before the deadline.", "我在截止日期前完成了。"),
            Vocab("schedule", "/ˈʃedjuːl/", "日程表", "What's on your schedule today?", "你今天的日程有什么？"),
        ),
        "I usually wake up early and review English for twenty minutes.",
        "我通常早起，然后复习二十分钟英语。",
        "每天固定同一时段学习，比“有空再学”更有效。",
    ),
    Lesson(
        2,
        "Work & projects",
        "工作与项目",
        "Talking about progress",
        "描述进展：I've finished / I'm working on",
        (
            Vocab("update", "/ˈʌpdeɪt/", "进展汇报", "Can you give me a quick update?", "能快速跟我同步一下吗？"),
            Vocab("blocker", "/ˈblɒkə/", "阻碍项", "The main blocker is missing data.", "主要阻碍是缺数据。"),
            Vocab("deliverable", "/dɪˈlɪvərəbl/", "交付物", "The first deliverable is due Friday.", "第一份交付物周五到期。"),
            Vocab("align", "/əˈlaɪn/", "对齐/协调", "Let's align on the next steps.", "我们先对齐下一步。"),
            Vocab("follow-up", "/ˈfɒləʊ ʌp/", "跟进", "I'll send a follow-up email.", "我会发一封跟进邮件。"),
        ),
        "I'm working on the report and will share an update tomorrow.",
        "我正在写报告，明天会同步进展。",
        "说进展时先结论，再补细节，英文邮件会更清晰。",
    ),
    Lesson(
        3,
        "Meetings",
        "会议沟通",
        "Polite interruptions and clarifying",
        "礼貌打断与确认理解",
        (
            Vocab("agenda", "/əˈdʒendə/", "议程", "What's the agenda for today?", "今天的议程是什么？"),
            Vocab("clarify", "/ˈklærɪfaɪ/", "澄清", "Could you clarify that point?", "能澄清一下这一点吗？"),
            Vocab("summarize", "/ˈsʌməraɪz/", "总结", "Let me summarize the key points.", "我来总结关键点。"),
            Vocab("takeaway", "/ˈteɪkəweɪ/", "结论/收获", "My takeaway is we need more tests.", "我的结论是我们需要更多测试。"),
            Vocab("action item", "/ˈækʃn ˌaɪtəm/", "待办事项", "Who owns this action item?", "这项待办谁负责？"),
        ),
        "Sorry to jump in — could you clarify the timeline?",
        "抱歉打断一下——能澄清一下时间线吗？",
        "听不懂时马上 clarify，比会后硬猜更专业。",
    ),
    Lesson(
        4,
        "Technology",
        "科技话题",
        "Explaining simple tech ideas",
        "用简单英文解释技术概念",
        (
            Vocab("feature", "/ˈfiːtʃə/", "功能", "This feature saves a lot of time.", "这个功能能省很多时间。"),
            Vocab("bug", "/bʌɡ/", "缺陷", "We fixed a critical bug yesterday.", "我们昨天修了一个严重缺陷。"),
            Vocab("deploy", "/dɪˈplɔɪ/", "部署上线", "We will deploy the update tonight.", "我们今晚会部署更新。"),
            Vocab("latency", "/ˈleɪtənsi/", "延迟", "Users complained about latency.", "用户抱怨延迟偏高。"),
            Vocab("reliable", "/rɪˈlaɪəbl/", "可靠的", "The service is more reliable now.", "这个服务现在更可靠了。"),
        ),
        "The new feature reduces latency and feels more reliable.",
        "新功能降低了延迟，用起来也更稳。",
        "解释技术时用“问题→改动→效果”三步，听众更容易懂。",
    ),
    Lesson(
        5,
        "News reading",
        "读新闻",
        "Skimming headlines for main idea",
        "快速抓住标题大意",
        (
            Vocab("headline", "/ˈhedlaɪn/", "标题", "The headline is a bit dramatic.", "这个标题有点夸张。"),
            Vocab("report", "/rɪˈpɔːt/", "报道", "According to the report, sales rose.", "据报道，销售额上升了。"),
            Vocab("claim", "/kleɪm/", "声称", "The company claims it is safe.", "公司声称它是安全的。"),
            Vocab("confirm", "/kənˈfɜːm/", "证实", "Officials confirmed the news.", "官方证实了这条消息。"),
            Vocab("source", "/sɔːs/", "消息来源", "The source was not named.", "消息来源未具名。"),
        ),
        "Skim the headline first, then decide if the story is worth reading.",
        "先扫标题，再决定这条值不值得细读。",
        "今天从邮件里的国际新闻挑 1 条英文标题，出声读两遍。",
    ),
    Lesson(
        6,
        "Opinions",
        "表达观点",
        "I think / In my view / It seems",
        "温和地表达看法",
        (
            Vocab("opinion", "/əˈpɪnjən/", "观点", "In my opinion, this is better.", "在我看来，这个更好。"),
            Vocab("prefer", "/prɪˈfɜː/", "更喜欢", "I prefer short meetings.", "我更喜欢短会。"),
            Vocab("agree", "/əˈɡriː/", "同意", "I agree with your point.", "我同意你的观点。"),
            Vocab("disagree", "/ˌdɪsəˈɡriː/", "不同意", "I disagree, but I see your point.", "我不同意，但我理解你的意思。"),
            Vocab("reasonable", "/ˈriːznəbl/", "合理的", "That sounds reasonable.", "听起来合理。"),
        ),
        "In my view, we should keep the plan simple.",
        "在我看来，我们应该把计划保持简单。",
        "不同意时先肯定对方一点，再给替代方案，语气会更稳。",
    ),
    Lesson(
        7,
        "Weekend review",
        "周末复盘",
        "Past simple for last week",
        "用一般过去时回顾一周",
        (
            Vocab("review", "/rɪˈvjuː/", "复盘/复习", "Let's review what we learned.", "我们复习一下学过的内容。"),
            Vocab("improve", "/ɪmˈpruːv/", "提升", "My speaking improved a little.", "我的口语有一点进步。"),
            Vocab("struggle", "/ˈstrʌɡl/", "吃力", "I struggled with listening.", "听力我听得比较吃力。"),
            Vocab("habit", "/ˈhæbɪt/", "习惯", "Consistency is a powerful habit.", "坚持是很强的习惯。"),
            Vocab("progress", "/ˈprəʊɡres/", "进步", "Small progress still counts.", "小进步也算进步。"),
        ),
        "Last week I reviewed vocabulary every morning.",
        "上周我每天早上都复习词汇。",
        "周末只做一件事：把本周 5 天单词各造一个自己的句子。",
    ),
    Lesson(
        8,
        "Travel basics",
        "出行基础",
        "Asking for help politely",
        "礼貌求助：Could you help me…?",
        (
            Vocab("direction", "/dəˈrekʃn/", "方向", "Could you give me directions?", "能给我指一下路吗？"),
            Vocab("reservation", "/ˌrezəˈveɪʃn/", "预订", "I have a reservation under Liu.", "我有一个姓刘的预订。"),
            Vocab("delay", "/dɪˈleɪ/", "延误", "The flight was delayed by an hour.", "航班延误了一小时。"),
            Vocab("luggage", "/ˈlʌɡɪdʒ/", "行李", "Where can I pick up my luggage?", "我在哪里取行李？"),
            Vocab("nearby", "/ˌnɪəˈbaɪ/", "附近的", "Is there a cafe nearby?", "附近有咖啡馆吗？"),
        ),
        "Excuse me, could you help me find gate B12?",
        "不好意思，能帮我找一下 B12 登机口吗？",
        "求助句先说 Excuse me，再把需求说清楚。",
    ),
    Lesson(
        9,
        "Health & habits",
        "健康习惯",
        "Giving advice with should / better",
        "用 should / you'd better 给建议",
        (
            Vocab("energy", "/ˈenədʒi/", "精力", "I have more energy after walking.", "走路后我精力更好。"),
            Vocab("stress", "/stres/", "压力", "Work stress affects my sleep.", "工作压力影响我的睡眠。"),
            Vocab("balance", "/ˈbæləns/", "平衡", "I need a better work-life balance.", "我需要更好的工作生活平衡。"),
            Vocab("stretch", "/stretʃ/", "拉伸", "I stretch for five minutes.", "我拉伸五分钟。"),
            Vocab("hydrate", "/ˈhaɪdreɪt/", "补水", "Don't forget to hydrate.", "别忘了喝水。"),
        ),
        "You should take a short walk when you feel stuck.",
        "卡住的时候，你应该出去走一小会儿。",
        "建议别人时用 should，语气比 must 柔和。",
    ),
    Lesson(
        10,
        "Money & markets",
        "金钱与市场",
        "Describing rises and falls",
        "描述涨跌：rose / fell / remained",
        (
            Vocab("price", "/praɪs/", "价格", "The gold price rose today.", "今天金价上涨了。"),
            Vocab("increase", "/ˈɪnkriːs/", "上升", "There was an increase in demand.", "需求有所上升。"),
            Vocab("decrease", "/ˈdiːkriːs/", "下降", "Sales showed a slight decrease.", "销售额略有下降。"),
            Vocab("volatile", "/ˈvɒlətaɪl/", "波动大的", "The market is very volatile.", "市场波动很大。"),
            Vocab("trend", "/trend/", "趋势", "What's the long-term trend?", "长期趋势是什么？"),
        ),
        "Gold rose slightly, while some tech stocks fell.",
        "黄金小幅上涨，而部分科技股下跌。",
        "结合今天邮件里的行情，试着用 rose/fell 各说一句。",
    ),
    Lesson(
        11,
        "Email writing",
        "写邮件",
        "Clear subject + short body",
        "主题明确，正文短",
        (
            Vocab("subject", "/ˈsʌbdʒɪkt/", "主题", "Keep the subject line clear.", "主题行要写清楚。"),
            Vocab("attach", "/əˈtætʃ/", "附件发送", "I attached the file below.", "我在下方附上了文件。"),
            Vocab("confirm", "/kənˈfɜːm/", "确认", "Please confirm if this works.", "请确认这样是否可以。"),
            Vocab("appreciate", "/əˈpriːʃieɪt/", "感谢", "I appreciate your help.", "感谢你的帮助。"),
            Vocab("regarding", "/rɪˈɡɑːdɪŋ/", "关于", "I'm writing regarding the invoice.", "我写信是关于发票的事。"),
        ),
        "Please confirm if you received the attached file.",
        "请确认你是否收到了附件。",
        "英文邮件三段就够：目的、细节、请求。",
    ),
    Lesson(
        12,
        "Listening skills",
        "听力训练",
        "Listen for keywords, not every word",
        "抓关键词，不必每个词都听清",
        (
            Vocab("accent", "/ˈæksent/", "口音", "I'm getting used to the accent.", "我在适应这个口音。"),
            Vocab("context", "/ˈkɒntekst/", "上下文", "Context helps me guess meaning.", "上下文帮我猜词义。"),
            Vocab("repeat", "/rɪˈpiːt/", "重复", "Could you repeat that, please?", "能请你再说一遍吗？"),
            Vocab("catch", "/kætʃ/", "听清/理解", "I didn't catch the last word.", "我没听清最后一个词。"),
            Vocab("podcast", "/ˈpɒdkɑːst/", "播客", "I listen to a short podcast daily.", "我每天听一个短播客。"),
        ),
        "I didn't catch that — could you repeat the key point?",
        "我没听清——能把关键点再说一遍吗？",
        "今天只听 3 分钟英文音频，目标是听出 3 个关键词。",
    ),
    Lesson(
        13,
        "Storytelling",
        "讲故事",
        "First / Then / Finally",
        "用顺序词把事情说完整",
        (
            Vocab("first", "/fɜːst/", "首先", "First, I checked the logs.", "首先，我查看了日志。"),
            Vocab("then", "/ðen/", "然后", "Then I restarted the service.", "然后我重启了服务。"),
            Vocab("finally", "/ˈfaɪnəli/", "最后", "Finally, the issue was fixed.", "最后问题修好了。"),
            Vocab("unexpected", "/ˌʌnɪkˈspektɪd/", "意外的", "We hit an unexpected error.", "我们遇到了意外错误。"),
            Vocab("result", "/rɪˈzʌlt/", "结果", "As a result, users can log in again.", "结果是用户又能登录了。"),
        ),
        "First I planned the day, then I studied, and finally I reviewed.",
        "我先规划一天，然后学习，最后复习。",
        "讲经历时用 First/Then/Finally，听的人不会迷路。",
    ),
    Lesson(
        14,
        "Midpoint review",
        "阶段复盘",
        "Present perfect: I've learned…",
        "现在完成时：我已经学了…",
        (
            Vocab("so far", "/səʊ fɑː/", "到目前为止", "So far, I've finished 13 lessons.", "到目前为止，我完成了 13 课。"),
            Vocab("confident", "/ˈkɒnfɪdənt/", "有信心的", "I feel more confident speaking.", "我开口时更有信心了。"),
            Vocab("challenge", "/ˈtʃælɪndʒ/", "挑战", "Listening is still a challenge.", "听力仍是个挑战。"),
            Vocab("practice", "/ˈpræktɪs/", "练习", "Daily practice beats long cramming.", "每天练，比突击更有效。"),
            Vocab("keep going", "/kiːp ˈɡəʊɪŋ/", "坚持下去", "Keep going even on busy days.", "忙的日子也要坚持。"),
        ),
        "So far I've learned useful phrases for work and daily life.",
        "到目前为止，我学了不少工作和生活里能用的表达。",
        "复盘只写三句：学会了什么、哪里难、下周怎么做。",
    ),
    Lesson(
        15,
        "Comparisons",
        "比较",
        "better than / as … as",
        "比较级与同级比较",
        (
            Vocab("compare", "/kəmˈpeə/", "比较", "Let's compare the two options.", "我们比较一下两个方案。"),
            Vocab("efficient", "/ɪˈfɪʃnt/", "高效的", "This way is more efficient.", "这种方式更高效。"),
            Vocab("similar", "/ˈsɪmələ/", "相似的", "The results are similar.", "结果差不多。"),
            Vocab("significant", "/sɪɡˈnɪfɪkənt/", "显著的", "There was a significant change.", "有显著变化。"),
            Vocab("slightly", "/ˈslaɪtli/", "略微", "Gold is slightly higher today.", "今天金价略高一点。"),
        ),
        "This method is better than waiting until the weekend.",
        "这个方法比拖到周末再学更好。",
        "比较时先说结论，再给一个具体理由。",
    ),
    Lesson(
        16,
        "Future plans",
        "未来计划",
        "I'm going to / I plan to",
        "谈论打算",
        (
            Vocab("plan", "/plæn/", "计划", "I plan to study after dinner.", "我计划晚饭后学习。"),
            Vocab("goal", "/ɡəʊl/", "目标", "My goal is to speak more fluently.", "我的目标是说得更流利。"),
            Vocab("prepare", "/prɪˈpeə/", "准备", "I need to prepare for the call.", "我需要为电话会议做准备。"),
            Vocab("expect", "/ɪkˈspekt/", "预期", "I expect it to take two weeks.", "我预计要两周。"),
            Vocab("soon", "/suːn/", "很快", "I'll start the next lesson soon.", "我很快开始下一课。"),
        ),
        "I'm going to review five words before bed tonight.",
        "我今晚睡前要复习五个单词。",
        "把“打算”说成具体动作，比只说 I will try 更有力量。",
    ),
    Lesson(
        17,
        "Problems & solutions",
        "问题与解决",
        "cause → effect → fix",
        "原因→影响→解决",
        (
            Vocab("issue", "/ˈɪʃuː/", "问题", "We found a small issue.", "我们发现了一个小问题。"),
            Vocab("cause", "/kɔːz/", "原因", "What caused the delay?", "延误的原因是什么？"),
            Vocab("solve", "/sɒlv/", "解决", "We solved it in an hour.", "我们一小时内解决了。"),
            Vocab("workaround", "/ˈwɜːkəraʊnd/", "临时方案", "There's a quick workaround.", "有个快速临时方案。"),
            Vocab("prevent", "/prɪˈvent/", "防止", "This can prevent future bugs.", "这能防止以后再出 bug。"),
        ),
        "The issue was caused by a timeout, and we fixed it with a retry.",
        "问题由超时引起，我们用重试修好了。",
        "描述故障时按“现象-原因-处理”说，对方更容易跟。",
    ),
    Lesson(
        18,
        "Customer / user talk",
        "用户沟通",
        "Empathy + next step",
        "先共情，再给下一步",
        (
            Vocab("feedback", "/ˈfiːdbæk/", "反馈", "Thanks for the feedback.", "感谢你的反馈。"),
            Vocab("experience", "/ɪkˈspɪəriəns/", "体验", "Sorry about the bad experience.", "抱歉给你不好的体验。"),
            Vocab("resolve", "/rɪˈzɒlv/", "妥善解决", "We'll resolve this today.", "我们今天会处理好。"),
            Vocab("urgent", "/ˈɜːdʒənt/", "紧急的", "Is this urgent?", "这件事紧急吗？"),
            Vocab("support", "/səˈpɔːt/", "支持", "Our support team will help you.", "我们的支持团队会帮你。"),
        ),
        "Sorry for the inconvenience. We'll resolve this and update you soon.",
        "抱歉带来不便。我们会处理好并尽快更新你。",
        "安抚句式先道歉，再给明确时间点。",
    ),
    Lesson(
        19,
        "Numbers & data",
        "数字与数据",
        "Saying percentages and changes",
        "说百分比与变化",
        (
            Vocab("percent", "/pəˈsent/", "百分之", "It rose by two percent.", "它上涨了百分之二。"),
            Vocab("average", "/ˈævərɪdʒ/", "平均", "The average score improved.", "平均分提高了。"),
            Vocab("roughly", "/ˈrʌfli/", "大约", "It costs roughly fifty dollars.", "大概五十美元。"),
            Vocab("exactly", "/ɪɡˈzæktli/", "恰好/精确地", "That's exactly what I meant.", "那正是我的意思。"),
            Vocab("figure", "/ˈfɪɡə/", "数字", "These figures look strong.", "这些数字看起来不错。"),
        ),
        "Nvidia rose by about half a percent today.",
        "英伟达今天大约上涨了百分之零点五。",
        "看今天行情，挑一只股票用 percent 造句。",
    ),
    Lesson(
        20,
        "Soft skills",
        "软技能",
        "Disagreeing politely",
        "礼貌地反对",
        (
            Vocab("respectfully", "/rɪˈspektfəli/", "恭敬地", "I respectfully disagree.", "我礼貌地表示不同意。"),
            Vocab("concern", "/kənˈsɜːn/", "顾虑", "I have one concern.", "我有一个顾虑。"),
            Vocab("alternative", "/ɔːlˈtɜːnətɪv/", "替代方案", "Here's an alternative.", "这是一个替代方案。"),
            Vocab("trade-off", "/ˈtreɪd ɒf/", "取舍", "Every choice has a trade-off.", "每个选择都有取舍。"),
            Vocab("compromise", "/ˈkɒmprəmaɪz/", "折中", "Can we find a compromise?", "我们能找到折中方案吗？"),
        ),
        "I see your point, but I have one concern about the timeline.",
        "我理解你的意思，但我对时间线有一个顾虑。",
        "反对句式：肯定 + but + 具体顾虑。",
    ),
    Lesson(
        21,
        "Weekly speaking",
        "口语周练",
        "2-minute self talk",
        "两分钟自言自语",
        (
            Vocab("fluent", "/ˈfluːənt/", "流利的", "I want to sound more fluent.", "我想说得更流利。"),
            Vocab("pause", "/pɔːz/", "停顿", "A short pause is okay.", "短暂停顿没关系。"),
            Vocab("pronounce", "/prəˈnaʊns/", "发音", "How do you pronounce this word?", "这个词怎么念？"),
            Vocab("record", "/rɪˈkɔːd/", "录音", "I record myself once a week.", "我每周给自己录一次音。"),
            Vocab("natural", "/ˈnætʃrəl/", "自然的", "It sounds more natural now.", "现在听起来更自然了。"),
        ),
        "Today I will talk about my work for two minutes without stopping.",
        "今天我要不停地说两分钟自己的工作。",
        "对着手机录音 2 分钟，只改最别扭的一句即可。",
    ),
    Lesson(
        22,
        "Idioms light",
        "轻量习语",
        "Common workplace idioms",
        "职场常用习语",
        (
            Vocab("on track", "/ɒn træk/", "按计划推进", "We're still on track.", "我们仍按计划推进。"),
            Vocab("at a glance", "/æt ə ɡlɑːns/", "一眼看清", "You can see it at a glance.", "一眼就能看清。"),
            Vocab("make sense", "/meɪk sens/", "说得通", "That makes sense.", "说得通。"),
            Vocab("wrap up", "/ræp ʌp/", "收尾", "Let's wrap up the meeting.", "我们结束会议吧。"),
            Vocab("keep in mind", "/kiːp ɪn maɪnd/", "记住", "Keep in mind the deadline.", "记住截止日期。"),
        ),
        "At a glance, the market looks mixed today.",
        "一眼看去，今天市场涨跌互现。",
        "习语先会用 1 个，比一次背 10 个更实用。",
    ),
    Lesson(
        23,
        "Reading longer text",
        "读长一点",
        "Topic sentence first",
        "先找主题句",
        (
            Vocab("paragraph", "/ˈpærəɡrɑːf/", "段落", "Read the first paragraph carefully.", "仔细读第一段。"),
            Vocab("main idea", "/meɪn aɪˈdɪə/", "主旨", "What's the main idea?", "主旨是什么？"),
            Vocab("detail", "/ˈdiːteɪl/", "细节", "Don't get lost in details.", "别沉进细节里。"),
            Vocab("infer", "/ɪnˈfɜː/", "推断", "We can infer the author is cautious.", "可以推断作者比较谨慎。"),
            Vocab("evidence", "/ˈevɪdəns/", "证据", "Where is the evidence?", "证据在哪里？"),
        ),
        "Find the main idea first, then look for supporting evidence.",
        "先找主旨，再找支持证据。",
        "挑今天一则英文摘要，用一句话写出 main idea。",
    ),
    Lesson(
        24,
        "Asking better questions",
        "更好的提问",
        "Open questions vs yes/no",
        "开放问题 vs 是否问题",
        (
            Vocab("specific", "/spəˈsɪfɪk/", "具体的", "Can you be more specific?", "能说得更具体吗？"),
            Vocab("example", "/ɪɡˈzɑːmpl/", "例子", "Could you give an example?", "能给个例子吗？"),
            Vocab("assume", "/əˈsjuːm/", "假设", "I assumed it was ready.", "我以为它已经好了。"),
            Vocab("verify", "/ˈverɪfaɪ/", "核实", "Let me verify the numbers.", "我来核实一下数字。"),
            Vocab("curious", "/ˈkjʊəriəs/", "好奇的", "I'm curious why that happened.", "我很好奇为什么会那样。"),
        ),
        "I'm curious — what made you choose this approach?",
        "我很好奇——你为什么选这个方法？",
        "开放问题用 what/why/how，对话会更深。",
    ),
    Lesson(
        25,
        "Time management",
        "时间管理",
        "for / since / until",
        "时间介词",
        (
            Vocab("focus", "/ˈfəʊkəs/", "专注", "I focus for 25 minutes.", "我专注二十五分钟。"),
            Vocab("distraction", "/dɪˈstrækʃn/", "干扰", "Phone alerts are a distraction.", "手机提醒是干扰。"),
            Vocab("postpone", "/pəˈspəʊn/", "推迟", "Don't postpone difficult tasks.", "别把难事往后拖。"),
            Vocab("until", "/ənˈtɪl/", "直到", "I'll study until 9 p.m.", "我会学到晚上九点。"),
            Vocab("since", "/sɪns/", "自从", "I've practiced since Monday.", "我从周一起就在练。"),
        ),
        "I've been studying English for twenty minutes every morning since last month.",
        "从上个月起，我每天早上都学二十分钟英语。",
        "for 接时长，since 接点时间，先分清这两个。",
    ),
    Lesson(
        26,
        "Culture & small talk",
        "文化与闲聊",
        "Safe small-talk openers",
        "安全的闲聊开场",
        (
            Vocab("weather", "/ˈweðə/", "天气", "The weather is nicer today.", "今天天气更好。"),
            Vocab("weekend", "/ˈwiːkend/", "周末", "How was your weekend?", "周末过得怎么样？"),
            Vocab("recommend", "/ˌrekəˈmend/", "推荐", "Can you recommend a book?", "能推荐一本书吗？"),
            Vocab("interest", "/ˈɪntrəst/", "兴趣", "I have an interest in history.", "我对历史感兴趣。"),
            Vocab("chat", "/tʃæt/", "闲聊", "Let's have a quick chat.", "我们随便聊两句。"),
        ),
        "How was your weekend? Did you get any rest?",
        "周末过得怎么样？休息到了吗？",
        "闲聊避开隐私和争议，从 weekend / weather 最稳。",
    ),
    Lesson(
        27,
        "Confidence",
        "建立自信",
        "Mistakes are data",
        "把错误当数据",
        (
            Vocab("mistake", "/mɪˈsteɪk/", "错误", "Mistakes help me improve.", "错误帮我进步。"),
            Vocab("nervous", "/ˈnɜːvəs/", "紧张的", "I get nervous before calls.", "打电话前我会紧张。"),
            Vocab("brave", "/breɪv/", "勇敢的", "Be brave and speak anyway.", "勇敢一点，还是说出来。"),
            Vocab("encourage", "/ɪnˈkʌrɪdʒ/", "鼓励", "Friends encourage me to practice.", "朋友鼓励我练习。"),
            Vocab("growth", "/ɡrəʊθ/", "成长", "This is part of my growth.", "这是我成长的一部分。"),
        ),
        "I still get nervous, but I speak anyway.",
        "我还是会紧张，但我还是会开口。",
        "今天故意说一句不完美的英文，只求完整不求完美。",
    ),
    Lesson(
        28,
        "Cycle review",
        "周期复盘",
        "What to keep doing next cycle",
        "下一轮继续做什么",
        (
            Vocab("consistent", "/kənˈsɪstənt/", "持续稳定的", "Be consistent, not perfect.", "要持续，不要完美主义。"),
            Vocab("reflect", "/rɪˈflekt/", "反思", "Reflect for three minutes daily.", "每天反思三分钟。"),
            Vocab("adjust", "/əˈdʒʌst/", "调整", "Adjust the plan if needed.", "需要就调整计划。"),
            Vocab("celebrate", "/ˈselɪbreɪt/", "庆祝", "Celebrate small wins.", "庆祝小胜利。"),
            Vocab("restart", "/ˌriːˈstɑːt/", "重新开始", "Tomorrow we restart the cycle.", "明天我们开启新一轮。"),
        ),
        "I've been consistent for four weeks, and I'll restart the cycle tomorrow.",
        "我坚持了四周，明天会开始新一轮。",
        "复盘后只保留一个习惯：每天打开这封邮件学 15 分钟。",
    ),
)


@dataclass
class EnglishPlan:
    day: int
    total_days: int
    lesson: Lesson
    title: str


def lesson_for_date(today: date) -> EnglishPlan:
    total = len(LESSONS)
    # Stable rotation by calendar day so the same date always gets the same lesson.
    day = ((today.toordinal() - 1) % total) + 1
    lesson = LESSONS[day - 1]
    title = f"英文学习 · 第 {day}/{total} 天 · {lesson.theme_zh}"
    return EnglishPlan(day=day, total_days=total, lesson=lesson, title=title)


def render_english_plain(plan: EnglishPlan) -> list[str]:
    lesson = plan.lesson
    lines = [
        f"【{plan.title}】",
        f"主题：{lesson.theme} / {lesson.theme_zh}",
        f"今日重点：{lesson.focus}（{lesson.focus_zh}）",
        "单词：",
    ]
    for index, word in enumerate(lesson.words, start=1):
        lines.append(f"{index}. {word.word} {word.phonetic} — {word.meaning}")
        lines.append(f"   {word.example}")
        lines.append(f"   {word.example_zh}")
    lines.extend(
        [
            "今日练习：",
            f"EN: {lesson.practice_en}",
            f"ZH: {lesson.practice_zh}",
            f"小提示：{lesson.tip}",
            "建议用时：15–20 分钟（朗读单词 → 跟读例句 → 口头说练习句）",
            "",
        ]
    )
    return lines


def render_english_html(plan: EnglishPlan) -> str:
    import html as html_lib

    lesson = plan.lesson
    word_rows = []
    for word in lesson.words:
        word_rows.append(
            f"""
            <tr>
              <td style="padding:8px 24px;border-top:1px solid #f0f0f0;">
                <div style="font-size:14px;font-weight:700;color:#111;">
                  {html_lib.escape(word.word)}
                  <span style="font-weight:400;color:#6b7280;font-size:12px;">{html_lib.escape(word.phonetic)}</span>
                  <span style="font-weight:400;color:#374151;"> — {html_lib.escape(word.meaning)}</span>
                </div>
                <div style="margin-top:4px;color:#111;font-size:13px;line-height:1.5;">{html_lib.escape(word.example)}</div>
                <div style="color:#6b7280;font-size:12px;">{html_lib.escape(word.example_zh)}</div>
              </td>
            </tr>
            """
        )
    return f"""
    <tr>
      <td style="padding:18px 24px 8px 24px;font-size:16px;font-weight:700;color:#111;border-top:1px solid #eee;background:#f8fafc;">
        {html_lib.escape(plan.title)}
      </td>
    </tr>
    <tr>
      <td style="padding:4px 24px 10px 24px;font-size:13px;color:#374151;line-height:1.6;">
        <div><b>主题：</b>{html_lib.escape(lesson.theme)} / {html_lib.escape(lesson.theme_zh)}</div>
        <div><b>今日重点：</b>{html_lib.escape(lesson.focus)}（{html_lib.escape(lesson.focus_zh)}）</div>
      </td>
    </tr>
    {''.join(word_rows)}
    <tr>
      <td style="padding:12px 24px 8px 24px;font-size:13px;color:#111;line-height:1.6;">
        <div style="font-weight:700;margin-bottom:4px;">今日练习</div>
        <div><b>EN:</b> {html_lib.escape(lesson.practice_en)}</div>
        <div style="color:#6b7280;"><b>ZH:</b> {html_lib.escape(lesson.practice_zh)}</div>
        <div style="margin-top:8px;color:#374151;"><b>小提示：</b>{html_lib.escape(lesson.tip)}</div>
        <div style="margin-top:6px;color:#9ca3af;font-size:12px;">建议用时 15–20 分钟：朗读单词 → 跟读例句 → 口头说练习句</div>
      </td>
    </tr>
    """
