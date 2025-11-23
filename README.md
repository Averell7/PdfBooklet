# PdfBooklet

PdfBooklet is a utility for creating booklets, manipulating PDF files, and preparing documents for precise and reliable printing workflows.

Originally developed to generate booklets from existing PDFs, it has evolved into a comprehensive tool that enables margin adjustment, scaling, rotation, merging, splitting, and page numbering. It is designed to solve common issues encountered with duplex printing, imposition, and document binding.

---

## Key Features

### Booklet Creation and Imposition
- **Multiple Booklets (Signatures):** Create a single booklet or split large PDFs into multiple signatures.
- **Flexible Imposition / Multi-Page Printing:** Arrange multiple pages per sheet (2-up, 4-up, custom rows and columns).
- **Supported Layouts:** Create both booklet (left-to-right) and calendar (top-to-bottom) layouts.
- **Custom Layout:** Define complex, user-defined layouts or manual imposition using page number lists.

### Page and File Manipulation
- **Merge and Split / Extract:** Merge PDF files or extract specific pages.
- **Visual Page Selector:** Drag-and-drop interface (pdf-shuffler based) to reorder, rotate, or delete pages.
- **Page Numbering:** Add page numbers.

### Transformations and Adjustments
- **Basic Transformations:** Adjust scale, margins, rotation, and shifts.
- **Auto-Scale:** Normalize page sizes.
- **Global and Per-Page Transformations:** Apply changes to all pages, a single page, even or odd pages.
- **Flip:** Flip pages vertically or horizontally.

### Interface and Workflow
- **Real-Time Preview:** Preview results accurately before exporting.
- **Project Saving:** Save and load project files (.ini) with settings and file lists.


---

## Requirements and Installation

PdfBooklet is built with Python and uses system libraries for PDF rendering and the graphical interface.

### Prerequisites (Debian/Ubuntu/Mint)

python3 python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-3.0 gir1.2-poppler-0.18

### Installation from Source

Clone the repository and install via the provided setup script (for .deb compatible installations).

PdfBooklet can also be executed directly from the source tree without installation.

---

## License

PdfBooklet is free/libre software. You are free to use, modify, and redistribute it under the terms of the **GNU General Public License v3 (GPL-3.0)**.
