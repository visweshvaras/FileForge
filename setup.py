from setuptools import setup, find_packages

setup(
    name="file-converter",
    version="1.0.0",
    description="Universal All-In-One Offline PDF & Media Workstation",
    author="Vishwa",
    license="MIT",
    packages=find_packages(),
    py_modules=["main"],
    install_requires=[
        "pymupdf>=1.24.0",
        "python-docx>=1.1.0",
        "python-pptx>=1.0.0",
        "openpyxl>=3.1.0",
        "pdf2docx>=0.5.8",
        "reportlab>=4.0.0",
        "pillow>=10.0.0",
        "yt-dlp>=2024.8.0",
        "mutagen>=1.47.0",
    ],
    entry_points={
        "console_scripts": [
            "file-converter=main:main",
        ],
    },
    python_requires=">=3.8",
)
