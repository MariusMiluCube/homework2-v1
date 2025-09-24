from re import split
from datasets import load_dataset
import random
from typing import Dict, List

LETTER_TO_INDEX = {'A': 0, 'B': 1, 'C': 2, 'D': 3}


class ArcService:
    '''
    Loads ARC-Easy and expose:
    - random_card() -> Dict
    - get_by_backend_id(backend_id: int) ->

    Returns stateless cards with:
        {
            id: str,
            backend_id: int,
            question: str,
            options: List[str],
            correct_index: int,
            explination: str
        }
    '''

    def __init__(self, split: str = 'train'):
        self.ds = load_dataset("ai2_arc", "ARC-Easy", split=split)
        if len(self.ds) == 0:
            raise ValueError('ARC-Easy split is empty.')

        self.rows: List[Dict] = []
        for i, row in enumerate(self.ds):
            card = self._shape_row_strict(i, row)
            self.rows.append(card)

    def _shape_row_strict(self, idx: int, row) -> Dict:
        qid = row.get('id') or str(idx)

        question = row.get('question')
        if not question or not isinstance(question, str):
            raise ValueError(f'Row {idx}: missing/invalid question')

        choices = row.get('choices') or {}
        texts = choices.get('text')
        labels = choices.get('label')

        if not isinstance(texts, list) or not isinstance(labels, list):
            raise ValueError(
                f'Row {idx}: choices.text/label missing or not lists')

        if len(texts) != len(labels) or len(texts) < 2:
            raise ValueError(
                f'Row {idx}: choice misaligned or too few {len(texts)}')

        pairs = []
        for t, lab in zip(texts, labels):
            if not isinstance(t, str) or not isinstance(lab, (str, int)):
                raise ValueError(f"Row {idx}: non-string choice or label")
            lab_str = str(lab).strip()
            if not lab_str:
                raise ValueError(f"Row {idx}: empty label")
            pairs.append((lab_str, t))

        def is_all_letters(ps): return all(p[0].isalpha() for p in ps)
        def is_all_digits(ps): return all(p[0].isdigit() for p in ps)

        if is_all_letters(pairs):
            pairs.sort(key=lambda p: p[0].upper())
        elif is_all_digits(pairs):
            pairs.sort(key=lambda p: int(p[0]))

        ordered_labels = [lab for lab, _ in pairs]
        options = [txt for _, txt in pairs]

        if len(options) < 2:
            raise ValueError(f"Row {idx}: fewer than 2 options after ordering")

        ans_key = row.get('answerKey')
        if ans_key is None:
            raise ValueError(f"Row {idx}: missing answerKey")

        ans_key_str = str(ans_key).strip()
        correct_index = None

        try_labels = [ans_key_str, ans_key_str.upper()]
        for cand in try_labels:
            if cand in ordered_labels:
                correct_index = ordered_labels.index(cand)
                break

        if correct_index is None:
            try:
                n = int(ans_key_str)
                if 0 <= n < len(options):
                    correct_index = n
                elif 1 <= n <= len(options):
                    correct_index = n-1
            except ValueError:
                pass

        if correct_index is None:
            raise ValueError(
                f"Row {idx}: cannot resolve answerKey={ans_key_str!r} "
                f"within labels={ordered_labels!r}"
            )

        return {
            'id': str(qid),
            'backend_id': idx,
            'question': question,
            'options': options,
            'correct_index': correct_index

        }

    def random_card(self) -> Dict:
        idx = random.randrange(len(self.rows))
        return self.rows[idx]

    def get_by_backend_id(self, backend_id: int) -> Dict:
        if not (0 <= backend_id < len(self.rows)):
            raise IndexError(f'backend_id {backend_id} out of range')
        return self.rows[backend_id]
