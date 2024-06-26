import math

import numpy as np
import torch
from torch.nn import functional as F

from lkan.utils.kan import fftkan

from .kan_linear import KANLinear
from .kan_linear_fft import KANLinearFFT


class KANConv2d(torch.nn.Module):
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        stride=1,
        padding=0,
        dilation=1,
        bias=True,
        grid_size=3,
        noise_scale=0.1,
        noise_scale_base=0.1,
        scale_spline=1.0,
        base_fun=torch.nn.SiLU(),
        sp_trainable=True,
        sb_trainable=True,
        chunk_size=None,
        device="cpu",
    ):
        super().__init__()
        self.kernel_size = kernel_size
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.stride = stride
        self.padding = padding
        self.dilation = dilation

        self.grid_size = grid_size
        self.base_fun = base_fun
        self.device = device
        self.chunk_size = chunk_size

        ##

        if scale_spline is not None:
            self.scale_spline = torch.nn.Parameter(
                torch.full(
                    (
                        self.in_channels,
                        out_channels,
                        kernel_size**2,
                    ),
                    fill_value=scale_spline,
                    device=device,
                ),
                requires_grad=sp_trainable,
            )
        else:
            self.register_buffer("scale_spline", torch.tensor([1.0], device=device))

        self.coeff = torch.nn.Parameter(
            torch.rand(
                self.in_channels,
                2,
                out_channels,
                kernel_size**2,
                grid_size,
                device=device,
            )
            * noise_scale
            / (np.sqrt(kernel_size**2) * np.sqrt(grid_size)),
        )  # [2, out_channels, kernel_size**2, grid_size]

        self.scale_base = torch.nn.Parameter(
            (
                1 / (kernel_size**2**0.5)
                + (
                    torch.randn(
                        self.in_channels,
                        self.out_channels,
                        self.kernel_size**2,
                        device=device,
                    )
                    * 2
                    - 1
                )
                * noise_scale_base
            ),
            requires_grad=sb_trainable,
        )

        ##

        if bias:
            self.bias = torch.nn.Parameter(
                torch.zeros(out_channels, device=device), requires_grad=True
            )
        else:
            self.bias = bias

        self.unfold = torch.nn.Unfold(
            kernel_size=kernel_size, stride=stride, padding=padding, dilation=dilation
        )

    def convolve(
        self,
        x,
        scale_base,
        scale_spline,
        coeff,
    ):
        shape = x.shape[:-1]
        x = x.view(-1, self.kernel_size**2)

        y = fftkan(
            x,
            scale_base,
            scale_spline,
            coeff,
            x.shape[0],
            self.kernel_size**2,
            self.out_channels,
            self.grid_size,
        )

        y = y.view(*shape, self.out_channels)

        return y

    def forward(self, x):
        shape = x.shape
        x = x.view(-1, shape[-3], shape[-2], shape[-1])  # [batch, in_channels, h, w]

        x = (
            self.unfold(x)  # [batch, patches, in_channels * kernel_size**2]
            .permute(0, 2, 1)  # [batch, in_channels * kernel_size**2, patches]
            .view(
                x.shape[0], -1, self.in_channels, self.kernel_size**2
            )  # [batch, patches, in_channels, kernel_size**2]
        ).contiguous()

        x = torch.vmap(self.convolve, (2, 0, 0, 0), 2, chunk_size=self.chunk_size)(
            x,
            self.scale_base,
            self.scale_spline,
            self.coeff,
        ).sum(dim=2)

        if self.bias is not False:
            x = x + self.bias[None, None, :]

        h = math.floor(
            (shape[-2] + 2 * self.padding - self.dilation * (self.kernel_size - 1) - 1)
            / self.stride
            + 1
        )
        w = math.floor(
            (shape[-1] + 2 * self.padding - self.dilation * (self.kernel_size - 1) - 1)
            / self.stride
            + 1
        )

        x = x.permute(0, 2, 1).view(*shape[:-3], self.out_channels, h, w)

        return x
