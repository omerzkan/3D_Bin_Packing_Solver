# 3D Bin Packing Solver

An intelligent optimization system that solves the bin packing problem in both **2D** and **3D** dimensions. This project combines advanced algorithmic solvers with interactive visualization and a user-friendly frontend interface.

## 🎯 Overview

The 3D Bin Packing Solver helps you optimize how items (boxes, cubes, or containers) fit inside a larger container. Whether you're working with 2D layouts or complex 3D environments, this tool provides efficient packing solutions using sophisticated algorithms.

### Key Features
- ✅ **2D Mode (bi-solver)**: Optimize rectangular items in a 2D space
- ✅ **3D Mode (three-solver)**: Solve complex 3D packing problems
- ✅ **Interactive Visualization**: Real-time visual feedback for packing solutions
- ✅ **Frontend Interface**: Intuitive UI for defining items and containers
- ✅ **Algorithmic Optimization**: Efficient solving with multiple algorithms

## 📋 Project Structure

```
3D_Bin_Packing_Solver/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── bi-solver/                   # 2D packing solver
├── three-solver/                # 3D packing solver
├── visualization/               # Visualization tools
├── frontend/                    # Web interface
└── docs/                        # Documentation
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/omerzkan/3D_Bin_Packing_Solver.git
cd 3D_Bin_Packing_Solver
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python main.py
```

## 💡 Usage

### 2D Bin Packing (bi-solver)
For packing rectangular items in a 2D space:

```python
from bi_solver import Packer2D

# Initialize 2D packer
packer = Packer2D(container_width=100, container_height=100)

# Add items
packer.add_item(width=50, height=30)
packer.add_item(width=40, height=40)

# Solve
solution = packer.solve()
```

### 3D Bin Packing (three-solver)
For packing items in a 3D container:

```python
from three_solver import Packer3D

# Initialize 3D packer
packer = Packer3D(width=100, height=100, depth=100)

# Add items
packer.add_item(width=50, height=30, depth=20)
packer.add_item(width=40, height=40, depth=30)

# Solve
solution = packer.solve()
```

### Visualization
Visualize your packing solution:

```python
from visualization import visualize_solution

visualize_solution(solution, mode='3D')  # or '2D'
```

## 🎨 Frontend

Access the interactive web interface:
1. Start the frontend server
2. Open your browser to `http://localhost:5000`
3. Define your container and items
4. Click "Solve" to get the optimal packing

## 📊 Algorithm Details

This project implements multiple bin packing algorithms:
- **First Fit Decreasing (FFD)**: Fast heuristic approach
- **Best Fit Decreasing (BFD)**: Optimized packing with better utilization
- **Guillotine Algorithm**: Effective for 2D and 3D packing
- **Genetic Algorithm** (optional): Advanced optimization

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 📈 Performance

- Handles containers and items efficiently
- Supports hundreds of items with real-time feedback
- Optimized for quick solution generation

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is available under the MIT License. See LICENSE file for details.

## 🆘 Support & Issues

Have questions or found a bug? 
- Open an [Issue](https://github.com/omerzkan/3D_Bin_Packing_Solver/issues)
- Check existing documentation
- Review closed issues for solutions

## 📚 Additional Resources

- [Bin Packing Problem](https://en.wikipedia.org/wiki/Bin_packing_problem)
- [Algorithm Documentation](./docs/algorithms.md)
- [API Reference](./docs/api.md)

## 👨‍💻 Author

**omerzkan** - [GitHub Profile](https://github.com/omerzkan)

## 🙏 Acknowledgments

Thanks to all contributors and the open-source community for making this project possible!

---

**Last Updated**: April 2, 2026