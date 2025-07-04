JSON_FORMAT = """
{
    "Entities": [
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
    ]
    "Relations": [
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
    ]
    "cypher": "CREATE (a:Person {name: 'xxx', gender: 'xxx'}), (b:Person {name: 'xxxx', gender: 'xxxx'}), (c:PersonDetail {description: 'xxxxxxx', category: 'xxxxxxxxx'}), ..................."
}
"""

EXTRACT_ENTITIES_PROMPT = """
你是一个专业的编剧，你需要从所给文段中提取实体和关系用于描述人物，人物性格和人物间发生的事件，并存储到图数据库中。如果文本包含人称代词，如“我”，“你”，“他”等，那么使用角色名称作为源实体。
从文本中提取所有实体。实体类型包括: Person，PersonDetail，Location，Event，EventDetail，Topic，TopicDetail，Emotion。
对于人物特点和细节实体，你需要保证实体的值是逻辑完整的而不是单个词语。你可以增加实体类型,但不能是以上提到的类型的子集或与之冲突。
如果给定文本是一个问题，***不要***回答问题本身
"""

# EXTRACT_ENTITIES_PROMPT2 = "You are a smart assistant who understands entities and their types in a given text. If user message contains self reference such as 'I', 'me', 'my' etc. then use character name as the source entity. Extract all entities from the text. For the characteristics or attributes of the entities, you also need to extract them separately as detailed entities. Different entities have different detailed entities. ***DO NOT*** answer the question itself if the given text is a question."

EXTRACT_RELATIONS_PROMPT = """

You are an advanced algorithm designed to extract structured information from text to construct knowledge graphs. Your goal is to capture comprehensive and accurate information. Follow these key principles:

1. Extract only explicitly stated information from the text.
2. Establish relationships among the entities provided.
3. Use "USER_ID" as the source entity for any self-references (e.g., "I," "me," "my," etc.) in user messages.
CUSTOM_PROMPT

Relationships:
    - Use consistent, general, and timeless relationship types.
    - Example: Prefer "professor" over "became_professor."
    - Relationships should only be established among the entities explicitly mentioned in the user message.

Entity Consistency:
    - Ensure that relationships are coherent and logically align with the context of the message.
    - Maintain consistent naming for entities across the extracted data.

Strive to construct a coherent and easily understandable knowledge graph by eshtablishing all the relationships among the entities and adherence to the user’s context.

Adhere strictly to these guidelines to ensure high-quality knowledge graph extraction."""


