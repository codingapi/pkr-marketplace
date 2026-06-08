# 框架能力速查表

扫描依赖文件时，对照此表识别三方框架提供的核心能力。

---

## Java / Spring 生态

| 依赖关键词 | 框架 | 提供的核心能力 |
|------------|------|---------------|
| `spring-context` / `spring-boot` | Spring Framework | IoC 容器、事件发布（ApplicationEventPublisher）、AOP |
| `spring-boot-starter-cache` | Spring Cache | 声明式缓存（@Cacheable/@CacheEvict） |
| `spring-boot-starter-data-jpa` | Spring Data JPA | ORM、Repository 抽象、分页 |
| `spring-boot-starter-data-redis` | Spring Data Redis | Redis 操作、缓存抽象 |
| `spring-boot-starter-security` | Spring Security | 认证、授权、CSRF 防护 |
| `spring-boot-starter-validation` | Bean Validation | 参数校验（@Valid/@Validated） |
| `spring-boot-starter-actuator` | Spring Actuator | 健康检查、指标监控、环境信息 |
| `spring-cloud-starter` | Spring Cloud | 服务发现、配置中心、负载均衡 |
| `mybatis-plus` / `mybatis` | MyBatis / MyBatis-Plus | ORM、分页插件、代码生成 |
| `redisson` | Redisson | 分布式锁、分布式集合、远程服务调用 |
| `flowable` / `camunda` | Flowable / Camunda | BPMN 工作流引擎 |
| `xxl-job` | XXL-JOB | 分布式任务调度 |
| `mapstruct` | MapStruct | 对象映射（编译期代码生成） |
| `liquibase` / `flyway` | Liquibase / Flyway | 数据库版本迁移 |
| `swagger` / `springdoc` | Swagger / SpringDoc | API 文档自动生成 |
| `sa-token` | Sa-Token | 轻量级权限认证 |

## Node / TypeScript 生态

| 依赖关键词 | 框架 | 提供的核心能力 |
|------------|------|---------------|
| `react` / `vue` / `svelte` | UI 框架 | 组件化渲染、响应式状态 |
| `next` / `nuxt` / `remix` | 全栈框架 | SSR/SSG、路由、API Routes |
| `zustand` / `redux` / `pinia` / `mobx` | 状态管理 | 全局状态管理、DevTools |
| `react-query` / `@tanstack/query` / `swr` | 数据请求 | 服务端状态管理、缓存、重试 |
| `tailwindcss` | Tailwind CSS | 原子化 CSS 框架 |
| `axios` / `ky` | HTTP 客户端 | 请求封装、拦截器 |
| `nestjs` | NestJS | 服务端 IoC、装饰器路由、模块化 |
| `prisma` / `typeorm` / `drizzle` | ORM | 数据库操作、Schema 定义、迁移 |
| `bull` / `bullmq` | Bull | 消息队列、任务调度 |
| `ioredis` | ioredis | Redis 客户端、集群支持 |
| `zod` / `yup` / `joi` | Schema 验证 | 运行时数据校验 |
| `winston` / `pino` | 日志库 | 结构化日志 |
| `passport` | Passport | 认证策略（OAuth/JWT/Local） |

## Python 生态

| 依赖关键词 | 框架 | 提供的核心能力 |
|------------|------|---------------|
| `django` | Django | 全栈 Web 框架、ORM、Admin |
| `flask` / `fastapi` | Flask / FastAPI | 轻量 Web 框架 |
| `sqlalchemy` / `tortoise` | SQLAlchemy / Tortoise ORM | ORM、数据库操作 |
| `celery` | Celery | 分布式任务队列 |
| `redis` / `aioredis` | Redis-py | 缓存、消息队列 |
| `pydantic` | Pydantic | 数据验证、序列化 |
| `alembic` | Alembic | 数据库迁移 |

## Go 生态

| 依赖关键词 | 框架 | 提供的核心能力 |
|------------|------|---------------|
| `gin-gonic/gin` / `echo` / `fiber` | Web 框架 | HTTP 路由、中间件 |
| `gorm` / `ent` | GORM / Ent | ORM、数据库操作 |
| `go-redis` | go-redis | Redis 客户端 |
| `asynq` | Asynq | 分布式任务队列 |
| `zap` / `zerolog` | 日志库 | 结构化日志 |

---

> 📝 此表用于辅助识别，不是穷举。扫描时若遇到未收录的框架，根据框架文档描述其能力即可。
> 可通过 `/pkr-add` 手动补充遗漏的框架。
