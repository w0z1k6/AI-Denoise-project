# scene02_white_snr5 去噪库选型落地说明

## 1) 结论

- 主推荐库：`DeepFilterNet`
- 备选库：`noisereduce`
- 当前场景不建议只用固定参数经典谱减作为最终方案

## 2) 选型证据（来自现有指标）

- 噪声类型是近白噪声宽带干扰：`noise_type = 近白噪声（宽带）`
- 高频带最差：`SNR(3400-8000Hz) = -8.50 dB`
- 局部极低 SNR 占比高：`ratio(SNR<0) = 89.66%`，`median local SNR = -24.15 dB`
- baseline 谱减残留仍明显：`residual RMS = 0.00805`，`kurtosis = 4.567`

这些特征说明该样本需要更强的时频自适应与语音结构建模能力，`DeepFilterNet` 比固定阈值方法更稳妥。

## 3) 何时用 DeepFilterNet，何时回退 noisereduce

- 使用 `DeepFilterNet`：
  - 目标是离线高质量降噪
  - 对辅音细节和高频听感有要求
  - 可以接受额外依赖与更高算力

- 使用 `noisereduce`：
  - 目标是快速批处理和低实现成本
  - 环境受限，优先稳定可运行
  - 用作第一版基线或工程 fallback

## 4) 可执行 AB 评估口径

统一输入：`noisy_testset/scene02_white_snr5.wav`

输出候选：

- `deepfilternet_out.wav`
- `noisereduce_out.wav`

评估目标：

- 主观：噪声明显下降，齿音和辅音不被明显抹平，无明显音乐噪声颗粒感
- 客观：
  - 高频带（3400-8000Hz）SNR 相对 noisy 输入有提升
  - 残留 RMS 低于 baseline
  - 残留 kurtosis 不高于 baseline，优先下降

## 5) 运行文件

- `run_scene02_noisereduce.py`：`noisereduce` 版本
- `run_scene02_deepfilternet.py`：`DeepFilterNet` 版本
- `eval_scene02_ab.py`：统一口径评估脚本

建议顺序：

1. 先跑 `noisereduce` 快速建立结果
2. 再跑 `DeepFilterNet` 作为主方案
3. 用评估脚本做 AB 对照
