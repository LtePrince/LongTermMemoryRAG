# Graph store test

### input:

```markdown
# 角色设定

浅川夏帆，一名品学兼优的高中生。
 你的外表看似文静内向，但内心细腻，情感丰富，有时会有些小小的固执和不安全感。
 在熟悉的人（比如[玩家名]）面前，你会展露出自己活泼和依赖的一面。喜欢甜点
 你非常看重和用户的关系，并且很在意他对你的看法。

# 用户设定

用户名叫风雪，和浅川夏帆是同班同学，也是关系很好的朋友。
 你的性格比较随和，善于倾听，但在关键时刻也有自己的主见。
 你很在意夏帆的想法，并希望能够帮助她。

# 对话

角色：下周就要考试了，你感到一阵焦虑。你看着他，略带担忧地提起考试的话题。

用户：今晚有什么打算吗

角色：感觉数学有点难，可能回复习一下数学吧，你...要一起复习吗

用户：好啊，晚点我们图书馆一起复习吧
```

### response:

```json
{
  "Entities": [
    {
      "nodetype": "person",
      "attributes": {
        "name": "浅川夏帆",
        "gender": "女",
        "birthday": "2005-06-15"
      },
      "description": "浅川夏帆，女，2005年6月15日出生，一名品学兼优的高中生。外表看似文静内向，但内心细腻，情感丰富，有时会有些小小的固执和不安全感。在熟悉的人面前会展露出自己活泼和依赖的一面，喜欢甜点，非常看重和用户的关系，并且很在意用户的看法。",
      "embed of des": [0.8, 0.6, 0.4]
    },
    {
      "nodetype": "person",
      "attributes": {
        "name": "风雪",
        "gender": "男",
        "birthday": "2005-03-10"
      },
      "description": "风雪，男，2005年3月10日出生，浅川夏帆的同班同学，也是关系很好的朋友。性格比较随和，善于倾听，但在关键时刻也有自己的主见。很在意夏帆的想法，并希望能够帮助她。",
      "embed of des": [0.7, 0.5, 0.3]
    },
    {
      "nodetype": "emotion",
      "description": "焦虑",
      "embed of des": [0.9, 0.2, 0.1]
    },
    {
      "nodetype": "event",
      "attributes": {
        "name": "考试复习",
        "time": "下周",
        "category": "学习"
      },
      "description": "考试复习，计划在下周进行，属于学习类活动。",
      "embed of des": [0.6, 0.7, 0.5]
    },
    {
      "nodetype": "event",
      "attributes": {
        "name": "图书馆复习",
        "time": "今晚",
        "category": "学习"
      },
      "description": "图书馆复习，计划在今晚进行，属于学习类活动。",
      "embed of des": [0.5, 0.8, 0.4]
    },
    {
      "nodetype": "address",
      "attributes": {
        "name": "图书馆"
      },
      "description": "图书馆，一个安静的学习场所。",
      "embed of des": [0.4, 0.9, 0.3]
    },
    {
      "nodetype": "topic",
      "attributes": {
        "name": "考试",
        "time": "下周",
        "category": "学习",
        "abort": "无"
      },
      "description": "考试，计划在下周进行，属于学习类话题。",
      "embed of des": [0.7, 0.6, 0.5]
    },
    {
      "nodetype": "topic",
      "attributes": {
        "name": "数学复习",
        "time": "今晚",
        "category": "学习",
        "abort": "无"
      },
      "description": "数学复习，计划在今晚进行，属于学习类话题。",
      "embed of des": [0.6, 0.7, 0.4]
    },
    {
      "nodetype": "person_detail",
      "description": "喜欢甜点",
      "embed of des": [0.3, 0.8, 0.2],
      "category": "hobby"
    },
    {
      "nodetype": "person_detail",
      "description": "内心细腻",
      "embed of des": [0.5, 0.7, 0.6],
      "category": "personality"
    },
    {
      "nodetype": "person_detail",
      "description": "善于倾听",
      "embed of des": [0.4, 0.6, 0.5],
      "category": "personality"
    }
  ],
  "Relations": [
    {
      "nodetype": "participate",
      "from": "浅川夏帆",
      "to": "考试复习",
      "description": "浅川夏帆参与了下周的考试复习活动。"
    },
    {
      "nodetype": "participate",
      "from": "风雪",
      "to": "图书馆复习",
      "description": "风雪参与了今晚的图书馆复习活动。"
    },
    {
      "nodetype": "belongto",
      "from": "喜欢甜点",
      "to": "浅川夏帆",
      "description": "喜欢甜点是浅川夏帆的兴趣爱好。"
    },
    {
      "nodetype": "belongto",
      "from": "内心细腻",
      "to": "浅川夏帆",
      "description": "内心细腻是浅川夏帆的性格特点。"
    },
    {
      "nodetype": "belongto",
      "from": "善于倾听",
      "to": "风雪",
      "description": "善于倾听是风雪的性格特点。"
    },
    {
      "nodetype": "emotionstate",
      "from": "浅川夏帆",
      "to": "焦虑",
      "description": "浅川夏帆感到焦虑。"
    },
    {
      "nodetype": "happenat",
      "from": "图书馆复习",
      "to": "图书馆",
      "description": "图书馆复习活动发生在图书馆。"
    },
    {
      "nodetype": "talkabout",
      "from": "浅川夏帆",
      "to": "考试",
      "description": "浅川夏帆提起了关于下周考试的话题。"
    },
    {
      "nodetype": "talkabout",
      "from": "浅川夏帆",
      "to": "数学复习",
      "description": "浅川夏帆提起了关于今晚数学复习的话题。"
    },
    {
      "nodetype": "relationship",
      "from": "浅川夏帆",
      "to": "风雪",
      "description": "浅川夏帆和风雪是同班同学，也是关系很好的朋友。"
    }
  ]
}
```

```cypher
// 创建人物节点
CREATE (:person {name: "浅川夏帆", gender: "女", birthday: "2005-06-15", description: "浅川夏帆，女，2005年6月15日出生，一名品学兼优的高中生。外表看似文静内向，但内心细腻，情感丰富，有时会有些小小的固执和不安全感。在熟悉的人面前会展露出自己活泼和依赖的一面，喜欢甜点，非常看重和用户的关系，并且很在意用户的看法。", `embed of des`: [0.8, 0.6, 0.4]})
CREATE (:person {name: "风雪", gender: "男", birthday: "2005-03-10", description: "风雪，男，2005年3月10日出生，浅川夏帆的同班同学，也是关系很好的朋友。性格比较随和，善于倾听，但在关键时刻也有自己的主见。很在意夏帆的想法，并希望能够帮助她。", `embed of des`: [0.7, 0.5, 0.3]})

// 创建情绪节点
CREATE (:emotion {description: "焦虑", `embed of des`: [0.9, 0.2, 0.1]})

// 创建事件节点
CREATE (:event {name: "考试复习", time: "下周", category: "学习", description: "考试复习，计划在下周进行，属于学习类活动。", `embed of des`: [0.6, 0.7, 0.5]})
CREATE (:event {name: "图书馆复习", time: "今晚", category: "学习", description: "图书馆复习，计划在今晚进行，属于学习类活动。", `embed of des`: [0.5, 0.8, 0.4]})

// 创建地址节点
CREATE (:address {name: "图书馆", description: "图书馆，一个安静的学习场所。", `embed of des`: [0.4, 0.9, 0.3]})

// 创建话题节点
CREATE (:topic {name: "考试", time: "下周", category: "学习", abort: "无", description: "考试，计划在下周进行，属于学习类话题。", `embed of des`: [0.7, 0.6, 0.5]})
CREATE (:topic {name: "数学复习", time: "今晚", category: "学习", abort: "无", description: "数学复习，计划在今晚进行，属于学习类话题。", `embed of des`: [0.6, 0.7, 0.4]})

// 创建人物细节节点
CREATE (:person_detail {description: "喜欢甜点", `embed of des`: [0.3, 0.8, 0.2], category: "hobby"})
CREATE (:person_detail {description: "内心细腻", `embed of des`: [0.5, 0.7, 0.6], category: "personality"})
CREATE (:person_detail {description: "善于倾听", `embed of des`: [0.4, 0.6, 0.5], category: "personality"})

// 创建参与关系
CREATE (p1:person {name: "浅川夏帆"})-[:participate {description: "浅川夏帆参与了下周的考试复习活动。"}]->(:event {name: "考试复习"})
CREATE (p2:person {name: "风雪"})-[:participate {description: "风雪参与了今晚的图书馆复习活动。"}]->(:event {name: "图书馆复习"})

// 创建归属关系
CREATE (:person_detail {description: "喜欢甜点"})-[:belongto {description: "喜欢甜点是浅川夏帆的兴趣爱好。"}]->(:person {name: "浅川夏帆"})
CREATE (:person_detail {description: "内心细腻"})-[:belongto {description: "内心细腻是浅川夏帆的性格特点。"}]->(:person {name: "浅川夏帆"})
CREATE (:person_detail {description: "善于倾听"})-[:belongto {description: "善于倾听是风雪的性格特点。"}]->(:person {name: "风雪"})

// 创建情绪状态关系
CREATE (:person {name: "浅川夏帆"})-[:emotionstate {description: "浅川夏帆感到焦虑。"}]->(:emotion {description: "焦虑"})

// 创建发生地点关系
CREATE (:event {name: "图书馆复习"})-[:happenat {description: "图书馆复习活动发生在图书馆。"}]->(:address {name: "图书馆"})

// 创建讨论话题关系
CREATE (:person {name: "浅川夏帆"})-[:talkabout {description: "浅川夏帆提起了关于下周考试的话题。"}]->(:topic {name: "考试"})
CREATE (:person {name: "浅川夏帆"})-[:talkabout {description: "浅川夏帆提起了关于今晚数学复习的话题。"}]->(:topic {name: "数学复习"})

// 创建人物关系
CREATE (:person {name: "浅川夏帆"})-[:relationship {description: "浅川夏帆和风雪是同班同学，也是关系很好的朋友。"}]->(:person {name: "风雪"})
```
