# runK Distillation Evaluation

- scenes: 15
- mean noisy SNR: 9.07 dB
- mean routed SNR: 12.69 dB
- mean runK refined SNR: 14.06 dB
- mean teacher SNR: 16.07 dB
- better than routed: 15/15
- mean RMS improve vs routed: 0.001386

| Scene | Noisy | Routed | runK | Teacher | RMS improve |
|---|---:|---:|---:|---:|---:|
| scene01_white_snr15 | 15.0 | 15.1 | 16.4 | 18.1 | 0.000857 |
| scene02_white_snr5 | 5.0 | 11.0 | 11.9 | 13.3 | 0.001020 |
| scene03_pink_snr10 | 10.0 | 12.9 | 14.1 | 16.5 | 0.001096 |
| scene04_brown_snr8 | 8.0 | 16.1 | 17.3 | 10.4 | 0.000694 |
| scene05_hum50_snr12 | 12.0 | 16.4 | 17.5 | 20.4 | 0.000674 |
| scene06_hum60_snr12 | 12.0 | 16.1 | 17.1 | 20.2 | 0.000600 |
| scene07_highfreq_hiss_snr10 | 10.0 | 14.7 | 16.0 | 18.8 | 0.000925 |
| scene08_lowfreq_rumble_snr10 | 10.0 | 14.4 | 15.8 | 18.2 | 0.000986 |
| scene09_chirp_interference_snr8 | 8.0 | 6.5 | 9.1 | 18.0 | 0.004364 |
| scene10_impulsive_clicks_snr9 | 9.0 | 12.5 | 13.5 | 15.1 | 0.000908 |
| scene11_intermittent_bursts_snr7 | 7.0 | 8.0 | 12.5 | 14.7 | 0.005695 |
| scene12_babble_like_snr5 | 5.0 | 8.2 | 8.8 | 10.3 | 0.000953 |
| scene13_street_combo_snr6 | 6.0 | 11.6 | 12.6 | 13.8 | 0.001011 |
| scene14_office_fan_snr9 | 9.0 | 13.1 | 13.3 | 15.8 | 0.000201 |
| scene15_reverb_plus_hiss_snr10 | 10.0 | 13.8 | 14.8 | 17.5 | 0.000807 |