---
name: springboot/cache
module: springboot
description: Spring Cache 声明式缓存，通过注解实现方法级缓存，无需手动管理缓存生命周期
status: 已实现
scope: 后端
source: 框架:spring
import: "org.springframework.boot:spring-boot-starter-cache"
framework_version: "3.2.0"
---

## 解决什么问题

业务层方法频繁查询数据库或远程服务，每次都重新计算会导致：

- 数据库查询压力
- 接口响应延迟
- 重复计算浪费资源

Spring Cache 提供声明式缓存能力，通过注解即可实现方法结果的自动缓存与失效。

## 如何使用

### 启用缓存

```java
@SpringBootApplication
@EnableCaching
public class Application {
}
```

### 核心注解

| 注解 | 用途 |
|------|------|
| `@Cacheable` | 方法结果缓存，命中则跳过执行 |
| `@CachePut` | 更新缓存，始终执行方法 |
| `@CacheEvict` | 清除缓存 |

### 配置

```yaml
spring:
  cache:
    type: caffeine
    caffeine:
      spec: maximumSize=500,expireAfterWrite=600s
```

## 使用实例

```java
@Cacheable(value = "users", key = "#userId")
public User getUser(Long userId) {
    return userRepository.findById(userId);
}

@CachePut(value = "users", key = "#user.id")
public User updateUser(User user) {
    return userRepository.save(user);
}

@CacheEvict(value = "users", key = "#userId")
public void deleteUser(Long userId) {
    userRepository.deleteById(userId);
}
```
