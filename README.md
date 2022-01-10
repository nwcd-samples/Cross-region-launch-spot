# 跨Region Launch spot解决方案

## 免责声明

建议测试过程中使用此方案，生产环境使用请自行考虑评估。

当您对方案需要进一步的沟通和反馈后，可以联系 nwcd_labs@nwcdcloud.cn 获得更进一步的支持。

欢迎联系参与方案共建和提交方案需求, 也欢迎在 github 项目 issue 中留言反馈 bugs。

---

当一个region的spot实例不足导致无法启动spot EC2实例时，启动临近region的EC2 spot实例，从而达到最佳性价比。本文假设使用region为Virginia，利用AWS跨region是骨干网的特性，在Virginia不能启动G4dn.xlarge实例时，从Ohio启动G4dn.xlarge实例。当Virginia的G4dn.xlarge实例有库存后，再逐渐将用量切回Virginia。

## 架构图

![架构图](./arch.png)

在us-east-1和us-east-2分别创建2个auto scaling group，分别名为virginiaASG和ohioASG。当us-east-1扩展spot G4失败时，触发lambda，将us-east-2的ASG扩展策略开启。默认生产环境在us-east-1的ASG，配置Cloudwatch rule当us-east-1的ASG中EC2实例启动失败，则通过lambda启动us-east-2上的ASG，并且关闭原有监测EC2实例启动失败的Cloudwatch rule，启动监测us-east-1的ASG中EC2启动成功的Cloudwatch Rule。当检测到us-east-1的ASG启动EC2实例成功，则通过Cloudwatch Rule关闭us-east-2的ASG，并且关闭原有监测EC2实例启动成功的Cloudwatch rule，启动监测us-east-1的ASG中EC2启动失败的Cloudwatch Rule。us-east-1 ASG使用更为精准的Metric，使用SQS的ApproximateNumberOfMessages值，除以ASG中In Service EC2数量，计算出每台EC2最佳处理任务的数量，使用target tracking scaling policy，使每台EC2处理任务保持最佳。us-east-2 ASG使用approximatenumberofmessagesvisible作为metric。

### 创建ASG用的Metric

us-east-1使用自定义Metric，根据官方文档https://docs.aws.amazon.com/zh_cn/autoscaling/ec2/userguide/as-using-sqs-queue.html，在使用SQS队列作为Metric，target tracking scaling作为策略时，建议使用每台EC2的处理任务数量作为Metric，获取方式如下：
使用 SQS获取队列属性 (https://docs.aws.amazon.com/cli/latest/reference/sqs/get-queue-attributes.html)命令获取在队列中等待的消息数 (ApproximateNumberOfMessages)
```
aws sqs get-queue-attributes --queue-url https://sqs.region.amazonaws.com/123456789/MyQueue \
--attribute-names ApproximateNumberOfMessages
```

使用 describe-auto-scaling-groups (https://docs.aws.amazon.com/cli/latest/reference/autoscaling/describe-auto-scaling-groups.html) 命令获取组的运行容量，这是处于 InService 生命周期状态的实例数。此命令返回 Auto Scaling 组的实例及其生命周期状态。
```
aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names my-asg

```

通过将可从队列中检索的消息的大概数量除以队列的运行容量，计算每个实例的任务数量。按照 1 分钟的粒度将结果发布为 CloudWatch 自定义指标。以下是示例将指标数据分析 (https://docs.aws.amazon.com/cli/latest/reference/cloudwatch/put-metric-data.html)命令。
```
aws cloudwatch put-metric-data --metric-name MyBacklogPerInstance --namespace MyNamespace \
--unit None --value 20 —dimensions MyOptionalMetricDimensionName=MyOptionalMetricDimensionValue

```

us-east-2使用approximatenumberofmessagesvisible作为metric，用如下命令获取，同样适用put-metric-data上传：
```
aws sqs get-queue-attributes --queue-url https://sqs.region.amazonaws.com/123456789/MyQueue \
--attribute-names ApproximateNumberOfMessagesvisile

```
### 创建ASG
我们假设每台EC2实例最佳处理任务数是20，同时预估us-east-1的ASG大约200台EC2实例规模。那么可以将us-east-1的ASG target tracking scaling自定义指标设置为20，将us-east-2的target tracking scaling自定义指标设置为200。由于target tracking scaling自定义的指标的ASG只能用命令行创建，参考：https://docs.aws.amazon.com/zh_cn/autoscaling/ec2/userguide/as-scaling-target-tracking.html#target-tracking-policy-creating-aws-cli

### 创建lambda：
将repo中的enable_ohio.py,disable_ohio.py,enable_rule.py,disable_rule.py分别创建为lambda funtion。

### 创建Cloudwatch rule：
如下图，当virginiaASG的EC2实例启动失败时，运行启动ohioASG的lambda，并且关闭当前cloudwatch rule，开启监控virginiaASG的EC2实例启动成功的cloudwatch rule。

反之，再创建一遍。
![cloudwatch](./cloudwatch.png)

部署完成。
