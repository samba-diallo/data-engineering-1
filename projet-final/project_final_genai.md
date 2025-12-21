# Generative AI Usage Documentation

**Project:** DE1 Final Project - Local Lakehouse  
**Author:** Badr TAJINI  
**Date:** Decembre 2025  

---

## 1. Declaration

This document describes how generative AI tools were used (or not used) in the completion of this Data Engineering I Final Project.

---

## 2. AI Tools Used

### 2.1 GitHub Copilot (VS Code Extension)
**Purpose:** Code assistance and project scaffolding  
**Usage Level:** Extensive  

#### Specific Use Cases:
1. **Project Structure Setup**
   - Generated initial directory structure for lakehouse layers (bronze/silver/gold)
   - Created comprehensive `de1_project_config.yml` with all required sections
   - Scaffolded notebook cells with proper markdown headers

2. **Code Generation**
   - PySpark DataFrame transformations for silver layer (schema application, type conversions)
   - Data quality validation logic from config rules
   - Physical plan capture and file I/O operations
   - Metrics logging and SLO validation code

3. **Documentation**
   - Generated report template with proper academic structure
   - Created inline code comments explaining optimization strategies
   - Drafted this GenAI usage documentation

#### What Was NOT Generated:
- **Business logic decisions:** Query definitions (Q1-Q3) were manually designed based on Wikipedia clickstream dataset analysis
- **SLO targets:** Service level objectives (4s latency, 60% storage) were set based on project requirements and 16GB RAM constraints
- **Optimization strategy:** Repartitioning and sorting by click count decisions were made through manual performance analysis
- **Metrics interpretation:** Performance analysis comparing baseline (19.4s) vs optimized (0.5s) done manually from Spark UI

---

## 3. Human Contributions

### 3.1 Design Decisions
All architectural decisions were made manually:
- **Dataset selection:** Chose Wikipedia Clickstream November 2024 based on size (10M rows, 450MB) and analytical relevance
- **Optimization strategy:** Selected repartitioning + sorting by click count (n DESC) after analyzing query patterns
- **Sort order:** Determined sortWithinPartitions by n descending for TOP-N query optimization
- **File sizing:** Calculated 128MB target based on 16GB RAM constraints and parallelism needs
- **Memory tuning:** Set driver.memory=4g, executor.memory=4g after encountering cache warnings

### 3.2 Testing and Validation
- **Notebook execution:** All cells were run manually to validate correctness
- **Error debugging:** Fixed schema mismatches and data quality issues through manual inspection
- **Performance measurement:** Captured Spark UI metrics by hand for each query run
- **SLO validation:** Manually compared baseline vs optimized metrics against targets

### 3.3 Critical Thinking
- **Optimization justification:** Analyzed physical plans to understand why optimizations worked
- **Trade-off analysis:** Evaluated partition count vs file size trade-offs
- **Limitation identification:** Recognized single-machine constraints and documented workarounds

---

## 4. AI Interaction Methodology

### 4.1 Prompting Strategy
Used specific, context-rich prompts:
```
Example: "Create PySpark code to apply schema from config YAML,
         enforce data quality rules, and log violations without emojis"
```

### 4.2 Code Review Process
Every AI-generated code snippet was:
1. **Reviewed:** Checked for correctness and PySpark best practices
2. **Tested:** Executed in notebook to validate functionality
3. **Adapted:** Modified to fit actual dataset schema and requirements
4. **Documented:** Added comments explaining why code exists

### 4.3 Limitations Encountered
- **Schema assumptions:** AI generated generic schemas; required manual adaptation to actual data
- **Query specificity:** AI couldn't know exact query requirements; queries were rewritten manually
- **Metric collection:** AI provided templates but couldn't access Spark UI; metrics filled manually

---

## 5. Learning Outcomes

### 5.1 Skills Developed Through AI Collaboration
- **Rapid prototyping:** Used AI to quickly scaffold structure, then refined manually
- **Code patterns:** Learned PySpark idioms from AI suggestions (e.g., `sortWithinPartitions`)
- **Documentation standards:** AI templates showed professional report structure

### 5.2 Skills Developed Independently
- **Performance analysis:** Learned to interpret Spark physical plans and UI metrics
- **Optimization techniques:** Understood partition pruning, file sizing, and AQE through experimentation
- **System design:** Designed lakehouse architecture based on DE1 course principles

---

## 6. Ethical Considerations

### 6.1 Academic Integrity
- **No plagiarism:** All AI-generated code was reviewed, understood, and adapted
- **Proper attribution:** This document transparently discloses AI usage
- **Original work:** Design decisions, analysis, and conclusions are original contributions

### 6.2 Collaboration Policy Compliance
This project follows ESIEE's policy on AI tool usage:
- AI used as a **productivity tool**, not a replacement for learning
- All work was **validated and understood** before submission
- **Critical thinking** applied to all AI suggestions

---

## 7. Conclusion

**AI Role:** Accelerator and scaffold generator  
**Human Role:** Designer, analyst, validator, and critical thinker  

Generative AI significantly improved development speed (estimated 40% time savings on boilerplate code), but all core engineering decisions, performance analysis, and optimization strategies were human-driven. This project demonstrates effective AI-human collaboration while maintaining academic integrity and deep technical understanding.

---

## 8. Appendix: AI-Generated Code Percentage

| Component | AI-Generated | Human-Written | Human-Adapted |
|-----------|--------------|---------------|---------------|
| Configuration YAML | 80% | 20% | 0% |
| Notebook code (bronze) | 60% | 20% | 20% |
| Notebook code (silver) | 50% | 30% | 20% |
| Notebook code (gold) | 40% | 40% | 20% |
| Optimization code | 30% | 50% | 20% |
| Report writing | 70% | 20% | 10% |
| GenAI documentation | 60% | 40% | 0% |

**Overall Estimate:** 55% AI scaffolding, 30% human original work, 15% human adaptation of AI code

---

**Signature:** Badr TAJINI  
**Date:** [Submission Date]  
**Affirmation:** I affirm that this document accurately represents the use of generative AI in this project.
