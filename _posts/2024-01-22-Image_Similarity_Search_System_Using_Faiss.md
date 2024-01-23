---
layout: post
title:  "Image Similarity Search System Using Faiss"
date:   2024-01-22
categories: jekyll update
tags: 
  - Database
  - Vector Database
  - Faiss
---

This system leverages vector databases, with a focus on Faiss, to efficiently return the most similar images from a database based on the input image. Vector databases manage high-dimensional data efficiently, and Faiss, developed by Facebook AI Research, is particularly adept at similarity search and clustering of dense vectors.

---

### Understanding Faiss Indices

Faiss offers a variety of index types, each optimized for specific scenarios and trade-offs in terms of memory usage, speed, and accuracy. At its core, Faiss uses quantization (the process of transforming a large, possibly infinite set of values into a smaller one) to compress vectors and reduce the computational intensity of the search.

**1. Flat Index (Brute Force Search)**

The simplest form of an index in Faiss is the flat index (`IndexFlatL2`). It performs an exhaustive search by comparing the query vector to every other vector in the database, using L2 distance (Euclidean distance).

**2. IVF (Inverted File) Index**

For larger datasets, an exhaustive search becomes impractical. The IVF index (`IndexIVFFlat`) improves the search efficiency by first clustering the dataset into `nlist` groups (quantization). During a search, only a subset of these groups, specified by `nprobe`, is examined. This significantly reduces the search time at the cost of a slight decrease in accuracy.

**How IVF Index Works:**

- **Training**: The IVF index requires a training phase, where it learns the distribution of the data by clustering the vectors into `nlist` clusters using the k-means algorithm.
- **Adding Vectors**: Once trained, the vectors are assigned to their nearest cluster, and only the cluster ID and residual vector (difference between the vector and its cluster centroid) are stored.
- **Searching**: During a search, the query vector is compared to a few cluster centroids (defined by `nprobe`), and only vectors in those clusters are considered for the final distance computation.

**3. PQ (Product Quantization) Index**

Product Quantization further compresses the vectors by dividing each vector into smaller sub-vectors and quantizing each sub-vector independently. Faiss implements PQ in indices like `IndexIVFPQ`. This method is highly memory efficient and allows for faster computation of distances but at the cost of lower accuracy.

**4. HNSW (Hierarchical Navigable Small World) Index**

HNSW is a graph-based index that builds a multi-layered structure where each layer forms a navigable small world graph. It provides a balance between search efficiency and accuracy, especially in high-dimensional spaces.

---

### Environment Setup

**Required Libraries**:

- Faiss: For efficient similarity search.
- Pillow: For image processing.
- Numpy: For numerical operations.
- PyTorch or TensorFlow: For feature extraction.

Installation command:

```bash
pip install faiss-cpu pillow numpy torch torchvision
# If you have GPU, install faiss-gpu
```

---

### Data Preparation

Prepare your image dataset and create an index table to record the ID and path of each image.

---

### Feature Extraction

Extract features from images using a pre-trained CNN model such as ResNet50.

```
import numpy as np
import faiss
from PIL import Image
import torchvision.transforms as transforms
from torchvision.models import resnet50
import torch

model = resnet50(pretrained=True)
model.eval()  # Set to evaluation mode

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def extract_features(img_path):
    img = Image.open(img_path)
    img_t = transform(img)
    batch_t = torch.unsqueeze(img_t, 0)
    
    with torch.no_grad():  # Disable gradient computation
        out = model(batch_t)
    features = out.detach().numpy().flatten()
    return features
```

---

### Building Faiss Index

Construct a Faiss index with feature vectors for efficient searching.

**Basic Index**:

```
import faiss
import numpy as np

d = 2048  # Feature dimension, matching the model output
index = faiss.IndexFlatL2(d)  # L2 distance-based flat index

for img_path, img_id in zip(img_paths, img_ids):
    features = extract_features(img_path)
    index.add(np.array([features]))  # Add to the index, must be a numpy array
```

**Advanced Index (e.g., IndexIVFFlat)**:

Faiss provides several indexing methods. Here we use `IndexIVFFlat`, an inverted file system with a flat quantizer. This is more efficient than a flat index for larger datasets.

```
nlist = 100
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)

index.train(db_vectors)  # db_vectors are your database vectors
index.add(db_vectors)
```

Before searching, you need to set the number of probes `nprobe`. This parameter defines how many clusters will be visited during search. A higher `nprobe` increases recall but also computational cost.

```
index.nprobe = 10
```

---

### Similarity Search

Perform fast similarity search using the Faiss index.

```
def search(img_path, k=5):
    query_features = extract_features(img_path)
    D, I = index.search(np.array([query_features]), k)  # Search
    return I  # Returns indices of the most similar images
```

---

### Result Presentation

Display the most similar images retrieved from the search.

```
def show_results(result_indices):
    for idx in result_indices[0]:
        img_path = img_paths[idx]
        img = Image.open(img_path)
        img.show()
```

---

### Performance Optimization

**Utilize GPU**:

Faiss supports GPU operations, which can significantly accelerate the indexing and searching process. Here's how you can use GPU resources in Faiss:

```
res = faiss.StandardGpuResources()  # Declare GPU resources
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)  # Move the index to GPU 0

D, I = gpu_index.search(query_vectors, k)  # Perform search on GPU
```

**Parameter Tuning**:

- Adjust `nlist` and `nprobe` parameters for an optimal balance between speed and accuracy.

**Batch Queries**:

- Stack multiple query vectors into a matrix for batch querying.

**Index Serialization**:

- Save and load the index for later use.

```
faiss.write_index(index, "path_to_save_index")  # Save the index
index = faiss.read_index("path_to_saved_index")  # Load the index
```

---

### Testing

Combine all components for testing.

```
result_indices = search('path_to_your_query_image.jpg')  # Test with your query image
show_results(result_indices)
```
