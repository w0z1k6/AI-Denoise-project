from __future__ import annotations

import numpy as np

from .base_omlsa_mcra import process as omlsa_process


def yule_walker_ar(x: np.ndarray, order: int = 10) -> np.ndarray:
    x = x.astype(np.float64)
    r = np.correlate(x, x, mode="full")
    mid = len(r) // 2
    ac = r[mid : mid + order + 1]
    R = np.empty((order, order), dtype=np.float64)
    for i in range(order):
        for j in range(order):
            R[i, j] = ac[abs(i - j)]
    rhs = ac[1 : order + 1]
    try:
        a = np.linalg.solve(R + 1e-6 * np.eye(order), rhs)
    except np.linalg.LinAlgError:
        a = np.linalg.pinv(R + 1e-6 * np.eye(order)) @ rhs
    return a.astype(np.float32)


def kalman_ar_filter(y: np.ndarray, order: int = 10) -> np.ndarray:
    coeff = yule_walker_ar(y, order=order)
    n = len(y)
    # State x_k = [s_k, s_{k-1}, ..., s_{k-order+1}]^T
    F = np.zeros((order, order), dtype=np.float32)
    F[0, :] = coeff
    if order > 1:
        F[1:, :-1] = np.eye(order - 1, dtype=np.float32)
    H = np.zeros((1, order), dtype=np.float32)
    H[0, 0] = 1.0

    # Coarse noise/process variance estimates.
    noise_var = float(np.var(y[: min(2000, n)]) + 1e-6)
    proc_var = noise_var * 0.2
    Q = proc_var * np.eye(order, dtype=np.float32)
    R = np.array([[noise_var]], dtype=np.float32)

    x_hat = np.zeros((order, 1), dtype=np.float32)
    P = np.eye(order, dtype=np.float32)
    out = np.zeros(n, dtype=np.float32)

    I = np.eye(order, dtype=np.float32)
    for k in range(n):
        # predict
        x_pred = F @ x_hat
        P_pred = F @ P @ F.T + Q
        # update
        z = np.array([[y[k]]], dtype=np.float32)
        S = H @ P_pred @ H.T + R
        K = P_pred @ H.T @ np.linalg.inv(S)
        x_hat = x_pred + K @ (z - H @ x_pred)
        P = (I - K @ H) @ P_pred
        out[k] = x_hat[0, 0]
    return out


def process(x: np.ndarray, sr: int) -> np.ndarray:
    y = kalman_ar_filter(x, order=10)
    # Post OMLSA to remove residual broad-band noise.
    return omlsa_process(y.astype(np.float32), sr)
