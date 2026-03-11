# 如何获取微信OpenID

## 方法1：通过微信公众号测试号管理页面（推荐）

1. 访问微信公众号测试号管理页面：
   https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login

2. 使用微信扫描页面上的二维码关注测试号

3. 关注后，页面会刷新，在页面向下滚动找到"用户列表"部分

4. 找到您的微信号，旁边会显示您的OpenID

5. 将OpenID复制到 `.env` 文件的 `WECHAT_OPENID` 配置项中

## 方法2：使用提供的脚本

如果您需要在代码中获取OpenID，可以运行：

```bash
# 注意：此方法需要公网访问或内网穿透
python3 get_openid.py
```

## 验证OpenID是否正确

获取OpenID后，可以运行测试脚本验证：

```bash
python3 test_wechat.py
```

如果看到 "新闻推送成功！请检查您的微信"，说明配置正确。

## 常见问题

### Q: OpenID格式是什么样的？
A: OpenID是一个字符串，通常以 `o` 开头，类似 `oXXXXXX` 的格式。注意：AppSecret和OpenID是完全不同的！

### Q: 为什么显示 "invalid openid" 错误？
A:
1. OpenID复制不完整
2. OpenID与AppSecret不匹配
3. 未关注测试号
4. 使用的是正式公众号的OpenID而非测试号的

### Q: 我已经关注了测试号，但找不到OpenID在哪里？
A:
1. 确保在测试号管理页面（不是普通公众号后台）
2. 向下滚动到页面底部
3. 找到"用户列表"区域
4. 您的微信号旁边就是OpenID

## 配置示例

.env文件配置示例：
```env
WECHAT_APPID=wxdd6ffcf441e469cd
WECHAT_APPSECRET=9d91cf64a0446b113b80b9d96dd6300b
WECHAT_OPENID=这里填写您的真实OpenID（不是AppSecret！）
```

**重要提示**：
- AppID = wxdd6ffcf441e469cd（应用ID）
- AppSecret = 9d91cf64a0446b113b80b9d96dd6300b（应用密钥）
- OpenID = 需要从测试号管理页面获取（用户身份标识）
