# 博客工作区

这里不是单纯的“博客文件夹”，而是整套博客连载的工作区。

它同时容纳：

- 专栏总览
- 写作规则
- 正式文章
- 草稿
- 选题池
- 给 Codex / Agent 使用的唯一入口文件

## 角色边界

- `00-博客Agent入口.md`
  - 博客写作的唯一工作入口
- `README.md`
  - 只做目录索引，不再重复维护命名规则、写作流程和输出位置规则

后续如果要让 Codex 或其他 Agent 总结每周内容并写博客，只需要让它先读取：

- [00-博客Agent入口.md](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/05-blog-posts/00-%E5%8D%9A%E5%AE%A2Agent%E5%85%A5%E5%8F%A3.md)

## 目录结构

```text
05-blog-posts/
├─ 00-博客Agent入口.md      # 唯一入口：给 Codex / Agent 的写作工作说明
├─ 01-写作规则/            # 固化的写作风格、语气和直发标准
├─ 02-专栏总览/            # 专栏介绍文、系列 README
├─ 03-正式文章/            # 已定稿、可直接发布的文章
├─ 04-草稿箱/              # 正在打磨中的文章
└─ 05-选题池/              # 待写主题、角度和素材沉淀
```

## 当前内容

- 写作规则：
  - [项目连载博客写作风格规范.md](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/05-blog-posts/01-%E5%86%99%E4%BD%9C%E8%A7%84%E5%88%99/%E9%A1%B9%E7%9B%AE%E8%BF%9E%E8%BD%BD%E5%8D%9A%E5%AE%A2%E5%86%99%E4%BD%9C%E9%A3%8E%E6%A0%BC%E8%A7%84%E8%8C%83.md)
- 专栏总览：
  - [2026-04-把-ai-开发练成真本事.md](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/05-blog-posts/02-%E4%B8%93%E6%A0%8F%E6%80%BB%E8%A7%88/2026-04-%E6%8A%8A-ai-%E5%BC%80%E5%8F%91%E7%BB%83%E6%88%90%E7%9C%9F%E6%9C%AC%E4%BA%8B.md)
- 草稿：
  - [2026-04-text-api-从能跑到像样的工程化收口.md](https://github.com/tzrea1-Q/ai-learning-bootcamp/blob/main/05-blog-posts/04-%E8%8D%89%E7%A8%BF%E7%AE%B1/2026-04-text-api-%E4%BB%8E%E8%83%BD%E8%B7%91%E5%88%B0%E5%83%8F%E6%A0%B7%E7%9A%84%E5%B7%A5%E7%A8%8B%E5%8C%96%E6%94%B6%E5%8F%A3.md)

命名规则、写作流程和输出位置规则统一见 `00-博客Agent入口.md`。
