# Parametric Weaving System (Grasshopper + GHPython)

A parametric design system that generates weaving patterns using alternating deformation, curve smoothing, and DataTree-based interpolation.

---

## 🧠 Concept

The system integrates geometric operations with DataTree manipulation to produce structured yet flexible patterns that can be applied to architectural elements such as:

- Facades  
- Canopies  
- Structural grids  

The core idea is to establish relationships between curves through **controlled deformation and tree alignment**.

---

## ⚙️ Workflow

1. Generate base curves  
2. Divide and deform points using an alternating pattern  
3. Construct smooth curves using fillet operations  
4. Generate tween points along each curve  
5. Shift DataTrees to establish relationships between adjacent branches  
6. Connect corresponding branches to produce weaving geometry  

---

## 🌳 Data Structure

The system relies on **Grasshopper DataTrees**:

- `{i}` → Curve index  
- `{i;j}` → Segment index  

Tree shifting is used to create **offset relationships** between branches, enabling the weaving logic.

---

## 🎛 Parameters

- `len_ln` → Base curve length  
- `height` → Vertical spacing between curves  
- `array_num` → Number of curves  
- `div_count` → Number of divisions per curve  
- `amplitude` → Deformation strength  
- `rad_fillet` → Curve smoothing radius  
- `tween_factor` → Interpolation density  
- `invert` → Flips deformation pattern globally  

---

## 🛠 Tools Used

- Grasshopper  
- GHPython (`ghpythonlib.components`)  

---
