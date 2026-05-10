# Assignment 2 - Generative AI Usage Documentation

**Authors:** DIALLO Samba, DIOP Mouhamed  
**Course:** Data Engineering I - ESIEE Paris  
**Date:** October 30, 2025  

---

## AI Tool Used

**Tool:** Claude Sonnet 4.5  
**Access Method:** GitHub Copilot Chat integration in VS Code  
**Usage Period:** Throughout Assignment 2 development

---

## How We Used Generative AI

### 1. Environment Setup and Configuration

**Task:** Setting up PySpark environment and PostgreSQL connection  
**AI Assistance:**
- Troubleshooting JAVA_HOME and SPARK_HOME configuration issues
- Resolving PostgreSQL JDBC driver integration
- Configuring Spark memory settings for large datasets (42M rows)

**Example Interaction:**
```
User: "How to connect Spark to PostgreSQL with read-only user?"
AI: Provided JDBC URL format and driver configuration code
```

### 2. Star Schema Design

**Task:** Designing dimensional model for retail data  
**AI Assistance:**
- Recommended surrogate key generation strategies
- Explained type-2 slowly changing dimension (SCD) concepts
- Suggested optimal grain for fact table

**Learning Outcome:** Understood difference between natural keys and surrogate keys, and why surrogate keys improve query performance.

### 3. Data Quality Implementation

**Task:** Implementing data validation rules  
**AI Assistance:**
- Suggested null checks and foreign key validation patterns
- Provided regex patterns for data cleaning
- Recommended handling of orphan records

**Code Example (AI-assisted):**
```python
# Validate foreign keys exist in dimensions
fact_with_valid_keys = fact_events.join(
    dim_user, 
    fact_events.user_key == dim_user.user_key, 
    "inner"
)
```

### 4. Performance Optimization

**Task:** Optimizing Spark jobs for 42M row dataset  
**AI Assistance:**
- Explained shuffle partitions configuration
- Recommended broadcast joins for small dimensions
- Suggested Parquet compression strategies

**Performance Gains:**
- Before optimization: 25 minutes execution time
- After AI-suggested tuning: 8 minutes execution time (68% improvement)

### 5. Code Debugging

**Task:** Resolving errors during ETL execution  
**AI Assistance:**
- Diagnosed "OutOfMemoryError" and suggested memory configurations
- Fixed "Column not found" errors in joins
- Resolved timezone issues in timestamp conversions

**Example Error Resolution:**
```
Error: java.lang.OutOfMemoryError: Java heap space
AI Solution: Increase spark.driver.memory to 4g and enable AQE
Result: Successfully processed all 42M rows
```

### 6. Documentation and Reporting

**Task:** Writing technical documentation  
**AI Assistance:**
- Structured REPORT.md outline
- Generated Markdown formatting examples
- Suggested visualizations for data flow diagrams

---

## What AI Did NOT Do

To maintain academic integrity, we ensured that:

1. **Core Logic:** All ETL logic and business rules were designed by us based on understanding of data engineering concepts
2. **Schema Design:** Star schema structure was designed independently after studying dimensional modeling principles
3. **Analysis:** Data quality assessments and performance comparisons were our own analysis
4. **Problem Solving:** When debugging, we first attempted to understand and solve issues before consulting AI

---

## Learning Outcomes

### Skills Developed with AI Assistance

1. **Faster Debugging:** AI helped identify root causes of errors quickly, allowing more time for learning core concepts
2. **Best Practices:** Learned industry-standard patterns for Spark optimization and dimensional modeling
3. **Documentation Skills:** Improved technical writing through AI-suggested structure and clarity

### Concepts Understood Through AI Explanations

1. **Surrogate Keys:** Why and when to use them in data warehousing
2. **Broadcast Joins:** How Spark optimizes joins with small dimension tables
3. **Parquet Columnar Storage:** Why it's more efficient than row-based CSV for analytics

---

## Transparency Statement

We believe in **transparent and ethical use of AI as a learning accelerator**. The AI assisted with:
- Technical troubleshooting (30% of time saved)
- Code optimization suggestions (improved understanding of Spark internals)
- Documentation structure (professional formatting)

However, the **core work** represents our understanding and application of:
- Data engineering principles
- ETL pipeline design
- Star schema dimensional modeling
- Apache Spark distributed processing

---

## Comparison: With vs Without AI

### Time Investment

| Task | Without AI (estimated) | With AI (actual) | Time Saved |
|------|----------------------|-----------------|------------|
| Environment Setup | 2 hours | 30 minutes | 75% |
| Schema Design | 4 hours | 3 hours | 25% |
| ETL Implementation | 8 hours | 6 hours | 25% |
| Debugging | 6 hours | 2 hours | 67% |
| Documentation | 3 hours | 1.5 hours | 50% |
| **Total** | **23 hours** | **13 hours** | **43%** |

### Quality Improvements

- **Code Quality:** AI suggested PEP-8 compliant formatting and best practices
- **Error Handling:** More robust error handling patterns
- **Performance:** 68% faster execution through AI-suggested optimizations

---

## Ethical Considerations

### Academic Integrity

We maintained academic integrity by:
1. Using AI as a **learning tool**, not a replacement for understanding
2. Always **validating** AI suggestions before applying them
3. **Crediting** AI assistance in documentation
4. Ensuring all deliverables reflect **our own understanding**

### Proper Attribution

All AI-assisted sections are documented in this file. We did not:
- Copy-paste AI-generated code without understanding
- Use AI to complete assignments without learning the concepts
- Misrepresent AI-generated work as entirely our own

---

## Conclusion

**Claude Sonnet 4.5** served as an effective **learning accelerator** for Assignment 2. It helped us:
- Debug faster, leaving more time for concept mastery
- Learn industry best practices early in our education
- Produce higher-quality, well-documented code

We believe this transparent approach to AI usage aligns with modern engineering practices where AI tools (like Copilot, ChatGPT, Claude) are standard productivity enhancers.

**Key Takeaway:** AI is a powerful tool for learning data engineering, but understanding the underlying concepts remains essential for professional competence.

---

**Authors:** DIALLO Samba, DIOP Mouhamed  
**Submission Date:** October 30, 2025  
**AI Tool:** Claude Sonnet 4.5 (via GitHub Copilot)
