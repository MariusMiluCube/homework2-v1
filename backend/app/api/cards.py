from fastapi import APIRouter, HTTPException
from ..models import Flashcard, AnswerRequest, AnswerResult
from ..services.cards import ArcService


router = APIRouter()
svc = ArcService(split='train')


@router.get('/random', response_model=Flashcard)
def random_card():
    try:
        card = svc.random_card()
        return Flashcard(**card)
    except ValueError as e:
        raise HTTPException(status_code=500, detail={
                            'error': 'dataset_integity', 'message': str(e)})


@router.post('/answer', response_model=AnswerResult)
def submit_answer(req: AnswerRequest):
    try:
        card = svc.get_by_backend_id(int(req.backend_id))
    except (IndexError, ValueError, TypeError):
        raise HTTPException(status_code=400, detail={
                            "error": "invalid_backend_id", "received": req.backend_id})

    ua = int(req.user_answer)
    if not isinstance(ua, int):
        try:
            ua = int(ua)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail={
                                "error": "invalid_user_answer", "received": req.user_answer})

    if ua < 0 or ua >= len(card['options']):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "answer_out_of_range",
                "message": f"user_answer must be between 0 and {len(card['options'])-1}.",
                "received": ua,
            },
        )

    ok = (ua == card['correct_index'])
    msg = "✅ Correct!" if ok else f"❌ Incorrect. Correct was {card['correct_index']}"
    return AnswerResult(correct=ok, correct_index=card["correct_index"], message=msg)
