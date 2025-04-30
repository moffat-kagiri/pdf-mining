import os
from multiprocessing import Pool
from tqdm import tqdm

# Define the processing function at the top level
def process_pdf(pdf_path_output):
    pdf_path, output_dir = pdf_path_output
    # Your PDF processing logic here
    # For example:
    print(f"Processing {pdf_path} into {output_dir}")
    # Simulate processing
    return f"Processed {pdf_path}"

def process_batch(pdf_paths, output_dir, workers):
    # Prepare arguments for the worker function
    pdf_path_output_pairs = [(pdf_path, output_dir) for pdf_path in pdf_paths]

    # Use multiprocessing with a top-level function
    with Pool(workers) as pool:
        results = list(tqdm(
            pool.imap(process_pdf, pdf_path_output_pairs),
            total=len(pdf_path_output_pairs),
            desc="Processing PDFs"
        ))

    print("Batch processing complete.")
    return results