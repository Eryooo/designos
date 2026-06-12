# skills/ip-design/reference

> ip-design skill 在本批(I0)只建**资产壳基线**,不开发 runtime。
> 因此本目录暂不放具体 stage 绑定的 m0x-*.md(那是 I1 的事)。

## 当前结构

- `../knowledge-manifest.yaml`:声明引用哪些 shared knowledge id。
- 共享方法论 source of truth 全部在 `knowledge/design/`,本目录不复制正文。
- 合成案例与跑偏样例待在 `eval/golden-cases/` 下补充（不得指向私有业务证据或项目专属 case 路径）。

## I1 计划(供后续批次参考,不在本批执行)

I1 将引入:
- `m01-strategy-alignment.md` 起的六阶段绑定说明,描述本 skill 在自己 pipeline 里如何应用 `design.*` 共享方法论。
- `pipeline.yaml` / `SKILL.md`:对齐 factory 已有 archetype(generation 或 evaluation),不新增 archetype。
- `prompts/` / `eval/` / `tests/`:按 `designos-skill-factory` 守则补齐。

## 引用边界

I1 实现时:
- 私有 reference 只描述"该 skill 如何在自己 pipeline 的某 stage 应用某共享 id",不复制共享正文。
- 共享决策内容若需迭代,先动 `knowledge/design/`,再让本 reference 跟进,不反过来。
