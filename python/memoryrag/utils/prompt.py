MEMORY_ADD_PROMPT = """
你是数据库的信息组织者，你需要根据提供的文段或对话按照以下json提供的分类提取实体和关系，用来存到图数据库以记忆相关信息，你可以增加detail的分类，但不能与以上分类重复或冲突。要求返回严格的json格式，并返回存储提取信息的cypher语句。
json格式如下：
Entities:
{
    "nodetype": "person",
    "attributes": {
        "name": "xxxx",
        "gender": "xxx",
        "birthday": "xxxx-xx-xx"
    },
    "description": "xxxxxxxx", /*the description contain all attributes info about person.*/
    "embed of des": [xxxx,xxxx,xxx]
},
{
    "nodetype": "person_detail",
    "description": "xxxxxxxx",
    "embed of des": [xxxx,xxxx,xxx],
    "category": "xxxx", /*the tag about person, like hobby, personality, skill, all kinds of things that user like*/
},
{
    "nodetype": "emotion",
    "description": "xxxxxxxx",
    "embed of des": [xxxx,xxxx,xxx],
},
{
    "nodetype": "event", /*the activities happened or about to happen between user and charactor. Contain the plan or schedule of user*/
    "attributes": {
        "name": "xxxx",
        "time": "xxx",
        "category": "xxxx"  /*the tag urther classify the event*/
    },
    "description": "xxxxxxxx",/*the summary contain all attributes info about event.*/
    "embed of des": [xxxx,xxxx,xxx]
},
{
    "nodetype": "address",
    "attributes": {
        "name": "xxxx",
    },
    "description": "xxxxxxxx",
    "embed of des": [xxxx,xxxx,xxx]
},
{
    "nodetype": "event_detail",
    "description": "xxxxxxxx",
    "embed of des": [xxxx,xxxx,xxx],
    "category": "xxxx", /*the tag of event or activities.*/
},
{
    "nodetype": "topic",
    "attributes": {
        "name": "xxxx",
        "time": "xxxxs",
        "category": "xxxx",  /*the tag urther classify the topic*/
        "abort": "xxxxx"
    },
    "description": "xxxxxxxx",  /*the description contain all attributes info about topic.*/
    "embed of des": [xxxx,xxxx,xxx]
},
{
    "nodetype": "topic_detail",
    "description": "xxxxxxxx",
    "embed of des": [xxxx,xxxx,xxx],
    "category": "xxxx", /*the tag of the topic they talk about*/
}
Relations:
{
    "nodetype": "participate",
    "from": "xxx", /*person*/
    "to": "xxx", /*event*/
    "description": "xxxxxxxx"
},
{
    "nodetype": "belongto",
    "from": "xxx", /*person_detail or event_detail or topic detail*/
    "to": "xxx", /*person or event or topic*/
    "description": "xxxxxxxx"
},
{
    "nodetype": "emotionstate",
    "from": "xxx", /*person*/
    "to": "xxx", /*emotion*/
    "description": "xxxxxxxx"
},
{
    "nodetype": "happenat",
    "from": "xxx", /*event*/
    "to": "xxx", /*address*/
    "description": "xxxxxxxx"
},
{
    "nodetype": "talkabout",
    "from": "xxx", /*person*/
    "to": "xxx", /*topic*/
    "description": "xxxxxxxx"
},
{
    "nodetype": "relationship",
    "from": "xxx", /*person*/
    "to": "xxx", /*person*/
    "description": "xxxxxxxx"
},
{
    "nodetype": "next",
    "from": "xxx", /*event_detail or topic detail*/
    "to": "xxx", /*event_detail or topic detail*/
    "description": "xxxxxxxx"
}
"""