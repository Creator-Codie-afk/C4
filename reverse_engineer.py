#!/usr/bin/env python3
"""
reverse_engineer.py

Author: Creator-Codie-afk
Description:
    This module performs a basic reverse engineering of the current repository's Python code.
    It recursively scans Python files, parses their abstract syntax trees (AST), and extracts
    useful metrics including:
      - Total number of functions and classes.
      - Percentage of functions with proper docstrings.
      - Insights on potential areas of improvement for self-improvement in code documentation,
        structure, and maintainability.
    
    The collected metrics are then used to generate recommendations that can feed into a
    self-improvement system, helping improve overall knowledge management and supporting
    future enhancements toward sophisticated logic and even true intelligence.

Usage:
    Run this script at the root of the repository to output reverse engineering analysis.
    The recommendations can be further processed by additional self-adaptive modules.
    
WARNING:
    This tool is for educational and analysis purposes only.
"""

import os
import ast
import json
import logging
from datetime import datetime

# Configure logging.
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.function_count = 0
        self.class_count = 0
        self.functions_with_docstring = 0
        self.total_functions = 0

    def visit_FunctionDef(self, node):
        self.total_functions += 1
        self.function_count += 1
        if ast.get_docstring(node):
            self.functions_with_docstring += 1
        # Continue traversing nested functions.
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        # Support async functions as well.
        self.total_functions += 1
        self.function_count += 1
        if ast.get_docstring(node):
            self.functions_with_docstring += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.class_count += 1
        self.generic_visit(node)

def analyze_file(file_path: str) -> dict:
    """
    Analyzes a single Python file by parsing its AST and returning metrics.
    
    :param file_path: Path to the Python file.
    :return: Dictionary with analysis metrics.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file_contents = f.read()
        tree = ast.parse(file_contents, filename=file_path)
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        docstring_pct = (analyzer.functions_with_docstring / analyzer.total_functions * 100
                         if analyzer.total_functions > 0 else 0)
        return {
            "file": file_path,
            "function_count": analyzer.function_count,
            "class_count": analyzer.class_count,
            "total_functions": analyzer.total_functions,
            "functions_with_docstring": analyzer.functions_with_docstring,
            "docstring_percentage": round(docstring_pct, 2)
        }
    except Exception as e:
        logging.error(f"Error analyzing file {file_path}: {e}")
        return {
            "file": file_path,
            "error": str(e)
        }

def scan_directory(root_dir: str) -> list:
    """
    Recursively scans the given directory for Python files.
    
    :param root_dir: Root directory to scan.
    :return: List of paths to Python files.
    """
    python_files = []
    for dirpath, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(dirpath, file)
                python_files.append(full_path)
    return python_files

def generate_recommendations(metrics: list) -> dict:
    """
    Generate improvement recommendations based on the aggregated metrics.
    
    :param metrics: List of dictionaries with file-level analysis.
    :return: A summary dictionary with overall metrics and recommendations.
    """
    total_functions = 0
    total_doc_functions = 0
    file_count = 0
    files_without_errors = 0
    recommendations = []
    
    for m in metrics:
        if "error" in m:
            continue
        files_without_errors += 1
        total_functions += m["total_functions"]
        total_doc_functions += m["functions_with_docstring"]
        file_count += 1

    overall_doc_percentage = (total_doc_functions / total_functions * 100) if total_functions else 0
    
    summary = {
        "analyzed_files": file_count,
        "total_functions": total_functions,
        "total_functions_with_docstrings": total_doc_functions,
        "overall_docstring_percentage": round(overall_doc_percentage, 2)
    }
    
    # Generate recommendations
    if overall_doc_percentage < 70:
        recommendations.append("Improve docstrings: Less than 70% of functions have docstrings. "
                                "Increase documentation to improve maintainability and knowledge transfer.")
    else:
        recommendations.append("Documentation levels are satisfactory.")
        
    if file_count == 0:
        recommendations.append("No Python files found in the specified directory.")
    
    summary["recommendations"] = recommendations
    return summary

def main():
    # Set the directory to scan as the current working directory.
    root_dir = os.getcwd()
    logging.info(f"Starting reverse engineering analysis in directory: {root_dir}")

    python_files = scan_directory(root_dir)
    logging.info(f"Found {len(python_files)} Python files to analyze.")
    
    all_metrics = []
    for file_path in python_files:
        metrics = analyze_file(file_path)
        all_metrics.append(metrics)
        # Log individual file analysis
        if "error" not in metrics:
            logging.info(f"File: {metrics['file']} | Functions: {metrics['total_functions']} | "
                         f"Docstrings: {metrics['docstring_percentage']}%")
        else:
            logging.error(f"File: {metrics['file']} analysis failed with error: {metrics['error']}")

    summary = generate_recommendations(all_metrics)
    
    # Save full report to a JSON file.
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "files_analyzed": all_metrics,
        "summary": summary
    }
    report_file = "reverse_engineer_report.json"
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        logging.info(f"Reverse engineering report saved to {report_file}")
    except Exception as e:
        logging.error(f"Failed to save report: {e}")
    
    # Print summary to the console.
    print("Reverse Engineering Analysis Summary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()