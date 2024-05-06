# Large Kolmogorov-Arnold Networks
Implementations of KAN variations.

Now I try train KAN on MNIST:
- I don't upgrade grid in kan - need update
- KAN - 96095 parameters, MLP - 101770 parameters
- is KAN slow in traning or initialization problem? MLP got 0.9 accuracy instant
- KAN around 120 it/s, MLP 210 it/s (almost 2x slower, need optimalization)
- MLP [784, 128, 10], KAN [784, 11, 10]
- On bigger KAN [784, 64, 10] i can't get good accuracy, i think is because of grid.

# Installation

```
pip install .
```

# Docs

See examples/ (in future)

# Problems
- [ ] small error in network output after update_grid (around 0.00232 max absolute difference between original model) - hard to reproduce.
- [ ] update_grid_from_samples in original KAN run model multiple times, is it necessary? 
- [ ] Unstable update_grid (loss explode).

# TODO/Ideas:
- [x] Base structure
- [x] KAN simple implementation
- [x] KAN trainer
- [x] train KAN on test dataset
- [x] remove unnecessary dependencies in requirements.txt
- [ ] test update_grid and "Other possibilities are: (a) the grid is learnable with gradient descent" from paper
- [ ] Regularization
- [ ] Compare with MLP
- [ ] Grid extension
- [ ] MNIST
- [ ] CIFAR10
- [ ] More datasets?
- [ ] KAN as CNN filter, KAN in VIT?
- [ ] Fourier KAN?
- [ ] pruning
- [ ] testing continual learning
- [ ] docs and examples - write notebooks like in KAN repo.
- [ ] KAN vs MLP in "LLM" - test?
- [ ] CUDA kernel for coeff2curve?

# Citations
```python
@misc{liu2024kan,
      title={KAN: Kolmogorov-Arnold Networks}, 
      author={Ziming Liu and Yixuan Wang and Sachin Vaidya and Fabian Ruehle and James Halverson and Marin Soljačić and Thomas Y. Hou and Max Tegmark},
      year={2024},
      eprint={2404.19756},
      archivePrefix={arXiv},
      primaryClass={cs.LG}
}
```