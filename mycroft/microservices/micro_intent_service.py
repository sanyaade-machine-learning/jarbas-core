from mycroft.skills.intent_service import IntentService, normalize, LOG


class MicroIntentService(IntentService):

    def handle_utterance(self, message):
        pass

    def get_intent(self, utterance, lang="en-us"):
        best_intent = None
        try:
            # normalize() changes "it's a boy" to "it is boy", etc.
            best_intent = next(self.engine.determine_intent(
                normalize(utterance, lang), 100,
                include_tags=True,
                context_manager=self.context_manager))
            # TODO - Should Adapt handle this?
            best_intent['utterance'] = utterance
        except Exception as e:
            LOG.exception(e)

        if best_intent and best_intent.get('confidence', 0.0) > 0.0:
            return best_intent
        else:
            return None
