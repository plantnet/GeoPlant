# 📦 Resources & Download

Access all key data, code, and paper links for the GeoPlant dataset and benchmarks.

---

## 🚀 Main Links

| Resource                  | Description                                                     | Link                                                                                                                                                      |
|---------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| 📄 **Dataset Paper**      | NeurIPS 2024 paper detailing the dataset and benchmark          | [NeurIPS Paper (PDF)](https://proceedings.neurips.cc/paper_files/paper/2024/file/e4e7de47202bda8133dd3e8b46205cf2-Paper-Datasets_and_Benchmarks_Track.pdf) |
| 🧠 **GitHub Repository**  | Codebase with data loaders, baseline models, and utilities      | [GeoPlant Repo](https://github.com/plantnet/GeoPlant)                                                                                                     |
| 🚀 **Starter Notebooks**  | Baseline models, pipelines, and scripts                        | [GeoPlant Code on Kaggle](https://www.kaggle.com/datasets/picekl/GeoPlant/code)                                                                           |
| 📦 **Full Dataset**       | Full data including PO and environmental rasters               | [GeoPlant Seafile](https://lab.plantnet.org/seafile/d/59325675470447b38add/)                                                                              |

---

## 🗃️ Dataset Download

- **Kaggle:** Download the *Presence-Absence* (PA) data and ready-to-use subsets directly.
- **Seafile:** Full dataset including all raw environmental rasters, images, and PO data.
- **HuggingFace:** Browse models and pretrained weights in [this collection](https://huggingface.co/collections/BVRA/geoplant-673da70e19bd21268a0f39a2).

---

## 💻 Code & Baselines

- **GitHub:** [plantnet/GeoPlant](https://github.com/plantnet/GeoPlant)  
  – PyTorch data loaders, training scripts, and evaluation code  
  – Fully reproducible baselines and benchmarks  
  – Issue tracker for questions and bug reports

- **Kaggle Code:**  
  Baseline notebooks for quick-start, all executable in-browser.

---

## 📚 Documentation

- **[Dataset Overview](dataset.md):** Details on PA/PO data, species coverage, and splits.
- **[Environmental Predictors](environmental_predictors.md):** All available modalities.
- **[Baselines & Benchmarking](baselines.md):** Tasks, metrics, and baseline performance.

---

## ❓ Questions or Issues?

- For dataset or technical questions, [open an issue](https://github.com/plantnet/GeoPlant/issues) on GitHub.
- For contribution, bug fixes, or ideas, create a pull request or discussion thread!

---

> **Tip:** For large downloads, prefer the zipped archives on Seafile. See ReadMe files inside each folder for detailed variable descriptions and file organization.

## 📑 Citation

If you use **GeoPlant** in your research or applications, please cite the dataset paper:

### BibTeX

```bibtex
@inproceedings{picek2024geoplant,
  title={GeoPlant: A Large-Scale Multimodal Dataset for High-Resolution Plant Species Prediction},
  author={Picek, Lukáš and Joly, Alexis and Servajean, Maximilien and Botella, Chris and others},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS) Datasets and Benchmarks Track},
  year={2024},
  url={https://proceedings.neurips.cc/paper_files/paper/2024/file/e4e7de47202bda8133dd3e8b46205cf2-Paper-Datasets_and_Benchmarks_Track.pdf}
}
```