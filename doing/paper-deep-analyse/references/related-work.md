# Related Work Expansion

目标：不是堆论文，而是把目标论文放进研究脉络中，找出前作、并行路线、替代方案和可迁移机会。

## 检索源优先级

1. 论文引用、arXiv HTML References、OpenReview reviews。
2. arXiv、ACL Anthology、NeurIPS/ICLR/ICML/CVPR 官方页面。
3. Semantic Scholar、Papers with Code、官方项目页、官方 GitHub。
4. 综述文章只作为导航，不作为唯一证据。

## 必查查询

- `<paper title> related work`
- `<core method name> arxiv`
- `<problem setting> reinforcement learning / agent / retrieval / tool use`
- `<main baseline name> vs <paper method name>`
- `<first author> <method keyword>`
- 引用链：目标论文 references 中最相关 5-10 篇。

## 分类方式

`notes/related-work-map.md` 不按时间平铺，按问题组织：

```markdown
# Related Work Map

## Problem lineage

| Problem | Prior route | This paper's route | Open question |
| --- | --- | --- | --- |

## Paper map

| Paper | Year | Source | Relation to target | Key difference | Link |
| --- | --- | --- | --- | --- | --- |
```

至少包含：

- 3 篇直接前作。
- 3 篇同问题替代路线。
- 2 篇同时期或后续相关工作；若无后续，说明检索日期和原因。
- 1 个代码/系统项目对照。

## 正文要求

HTML 中必须有“研究脉络”或“相关论文发散”章节，至少比较 6 篇相关工作。比较要回答：

- 它们解决的是同一问题、相邻问题，还是工具/实验设置相似？
- 本文相对它们的新增变量是什么？
- 本文没有覆盖但相关工作覆盖了什么？
- 哪条路线最值得继续做？

