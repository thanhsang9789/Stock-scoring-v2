import yaml
import logging

def load_config(filepath: str) -> dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('StockScoreV2')
