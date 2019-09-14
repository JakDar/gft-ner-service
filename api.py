from concurrent import futures
import grpc
import time
import generated.ner_pb2 as proto
import generated.ner_pb2_grpc as proto_grpc
from logging import Logger
import en_core_web_lg
from spacy.tokens.span import Span
from typing import Tuple
from functional import seq

nlp = en_core_web_lg.load()


def get_entities(text: str) -> Tuple[Span]:
    parsed = nlp(text)
    return parsed.ents


ner_mapping = {
    "PERSON": proto.NerType.PERSON,
    "FACILITY": proto.NerType.FACILITY,
    "FAC": proto.NerType.FACILITY,
    "LAW": proto.NerType.LAW,
    "ORG": proto.NerType.ORG,
    "MONEY": proto.NerType.MONEY,
    "GPE": proto.NerType.GPE,
    "LOC": proto.NerType.LOC,
    "QUANTITY": proto.NerType.QUANTITY,
    "CARDINAL": proto.NerType.CARDINAL,
    "DATE": proto.NerType.DATE,
    "PERCENT": proto.NerType.PERCENT,
    "TIME": proto.NerType.TIME,
    "PRODUCT": proto.NerType.PRODUCT,
    "NORP": proto.NerType.NORP,
}


def label_to_proto(logger: Logger, label: str, text: str) -> proto.NerType:
    if label in ner_mapping.keys():
        return ner_mapping[label]
    else:
        logger.warn("Unsupported ner label {} for text {}".format(label, text))
        return proto.NerType.OTHER


class NerService(proto_grpc.NerServiceServicer):
    def __init__(self, logger: Logger):
        self.logger = logger

    def GetEnglishNers(self, request, context):
        try:

            results = seq(get_entities(request.text)).map(
                lambda span: proto.NerEntry(
                    text=span.text,
                    nerType=label_to_proto(
                        self.logger, label=span.label_, text=span.text
                    ),
                )
            )

            return proto.GetEnglishNersResponse(entities=results)

        except Exception as ex:
            self.logger.exception(ex)
            raise ex


def serve(port: int, logger: Logger) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    proto_grpc.add_NerServiceServicer_to_server(NerService(logger), server)
    server.add_insecure_port("[::]:{}".format(port))
    server.start()
    logger.info("Server started at port {}".format(port))

    try:
        while True:
            time.sleep(24 * 60 * 60)
    except KeyboardInterrupt:
        server.stop(0)
