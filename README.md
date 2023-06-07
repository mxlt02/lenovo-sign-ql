# lenovo-sign-ql
联想智选签到-青龙专版

**使用须知：**  
**1. 使用的Python版本必须大于等于Python3.8**  
**2. 定时执行的任务必须放到中午十二点以后（推荐中午十二点），本人在早上八九点测试有问题**

已支持每日自动刷新签到时间功能

## 青龙面板使用

1. 安装脚本依赖`requests toml`
2. 添加订阅 ql repo https://ghproxy.com/https://github.com/mxlt02/lenovo-sign-ql.git "lenovo_sign.py"
3. cron使用0 0 * * * ，手动运行订阅
4. 把文件`config.toml`, `sendNotify.py`上传到青龙面板刚刚运行订阅后生成的脚本文件夹mxlt02_lenovo-sign-ql应该是这个
5. 在`config.toml`里面填写账号
6. 完成！进行测试
