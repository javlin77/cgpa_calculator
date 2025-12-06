# 🎓 SGPA & CGPA Calculator

A clean and interactive **Streamlit-based** web application that helps students calculate their **SGPA (Semester Grade Point Average)** and **CGPA (Cumulative Grade Point Average)** using the standard **10-point grading system**.

This tool is designed to make academic grade calculation simple, fast, and error-free.  
Students can enter subjects, credits, and grades for each semester—and the app automatically computes SGPA and the overall CGPA.

---

## 🚀 Features

### **Streamlit UI**
A smooth and responsive interface built entirely with **Streamlit**, offering:
- Fast load times  
- Clean layout  
- Automatic recalculations  
- Modern dark theme  

### **10-Point Grading System**
The calculator follows the common grading scheme:

| Grade | Points |
|-------|--------|
| O     | 10     |
| A+/E  | 9      |
| A     | 8      |
| B     | 7      |
| C     | 6      |
| D     | 5      |
| D'    | 4      |
| F     | 2      |
| I     | 0      |


### **Multiple Semester Support**
You can:
- Add several semesters  
- Modify or replace a semester’s values  
- Automatically compute cumulative CGPA  

### **Clear UI Components**
- Subject-wise entry  
- Grade selection  
- Credit-based evaluation  
- Live SGPA and CGPA display  
- Expandable tables showing all calculations  

---

## 🧮 Want to verify with another marking scheme?

This project is designed around the **10-point CGPA model**, but if you're interested in experimenting with **different grading systems**, you can modify the grade–point mapping inside the code.

The structure is modular, so anyone can tweak:
- Grade symbols  
- Point values  
- Calculation formulas  

Feel free to explore the logic and adapt it to your own institution's grading style.

---

## ▶️ Run Locally

```bash
pip install streamlit pandas
streamlit run app.py
