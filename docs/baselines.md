# 🏁 Baselines & Benchmarking

GeoPlant provides a variety of strong and weak baselines for plant species distribution modeling, using both conventional ML and deep learning approaches. All code is available on [GitHub](https://github.com/plantnet/GeoPlant) and as reproducible Kaggle notebooks.

## 💡 Benchmark Tasks

- **Presence-Absence (PA) prediction:** Predict the set of species present in a plot (multi-label).
- **Presence-Only (PO) experiments:** (see Appendix) More challenging, due to missing absences.

Evaluation Metrics:  
- **AUC**, **Recall**, **Sample-Averaged F1 ($F_1^s$)**, and Precision  
- Most results are reported for the *top-25 predicted species per plot*.

---

## 🪄 Naive Baselines

Naive predictors select the most common species for a given region or administrative district.  
- *Top-25 most common species per district*: **$F_1^s$ = 20.6%** (PA), **<9%** (PO)

---

## 🔥 Single-Modality Deep Learning Baselines

| Model        | Modality         | AUC    | Recall | F1<sup>s</sup> |
|--------------|------------------|--------|--------|---------------|
| **MLP**      | Climatic Cubes   | 82.8   | 32.1   | 22.2          |
|              | Landsat Cubes    | 82.6   | 42.0   | 28.4          |
|              | Sentinel-2 Img   | 71.8   | 23.2   | 15.8          |
| **ResNet-6** | Climatic Cubes   | 91.8   | 37.5   | 26.2          |
|              | Landsat Cubes    | 92.1   | 44.8   | 30.3          |
|              | Sentinel-2 Img   | 87.3   | 32.1   | 22.0          |
| **ResNet-18**| Climatic Cubes   | 90.5   | 37.8   | 26.2          |
|              | Landsat Cubes    | 91.8   | 44.2   | 29.9          |
|              | Sentinel-2 Img   | 88.6   | 33.2   | 22.7          |

*All scores averaged over 5 random seeds, PA data only.*

---

## 🤖 Conventional ML Baselines

**XGBoost** and **MaxEnt** were tested with up to four predictors (location, climate, soilgrids, land cover).

| Model    | Predictors Used           | AUC   | Recall | F1<sup>s</sup> |
|----------|--------------------------|-------|--------|---------------|
| XGBoost  | Location only            | 89.8  | 47.6   | 28.2          |
| XGBoost  | Climatic only            | 88.9  | 46.1   | 26.7          |
| XGBoost  | Location + Clim + Soil + LC | 90.4  | 48.8   | 28.7          |
| MaxEnt   | All (492 species only)   | -     | -      | ~0.17-0.18    |

*XGBoost outperforms MaxEnt, but both lag behind deep multimodal models.*

---

## 🏆 Multimodal Ensemble Baselines

Combining modalities (climatic + landsat + satellite images) via an ensemble of encoders (ResNet-6) further improves results.

| Model                      | Modalities                   | AUC   | Recall | F1<sup>s</sup> |
|----------------------------|------------------------------|-------|--------|---------------|
| MME                        | Clim + Landsat               | 93.6  | 49.3   | 33.8          |
| MME                        | Clim + Landsat + Sentinel-2  | 94.0  | 49.7   | 34.1          |
| MME + Top-K Estimation     | Clim + Landsat               | 93.6  | 45.0   | 35.9          |
| MME + Top-K Estimation     | Clim + Landsat + Sentinel-2  | 94.0  | 45.3   | 36.2          |

**Diagram:**
![Multimodal Ensemble Model](assets/mme-graphical.png)
*Each modality (cube/image) is encoded, concatenated, and classified jointly.*

---

## 💡 Additional Insights

- **Top-K selection:** Optimal number of species per survey is $k=20$–$30$ for cubes, $k=25$ for climate data.
- **Presence-Only (PO) Data:** Training on PO and testing on PA gives much lower $F_1^s$ (as low as 8–15% for deep models).
- **Best Single Modality:** Landsat cubes outperform Sentinel-2 images and climate alone.

---

## 📈 How to Reproduce?

- All experiments are in [plantnet/GeoPlant](https://github.com/plantnet/GeoPlant) and on [Kaggle](https://www.kaggle.com/datasets/picekl/GeoPlant/code).
- Training logs: [Weights & Biases](https://wandb.ai/picekl/GeoPlant)

---

## 📋 Table Legend

- **AUC:** Area Under ROC Curve (binary per species, averaged).
- **Recall:** Fraction of true species found in top-25 predictions.
- **F1<sup>s</sup>:** Sample-averaged F1-score (across test plots, top-25 predictions).

---

