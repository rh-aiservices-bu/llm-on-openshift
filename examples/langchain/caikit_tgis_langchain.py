import sys
sys.path.insert(0, "./pb2")
from nlpservice_pb2_grpc import NlpServiceStub
import nlpservice_pb2
import grpc

from typing import Any, List, Mapping, Optional, Iterator
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.schema.output import GenerationChunk


class CaikitLLM(LLM):
    inference_server_url: str
    model_id: str
    nlp_service_stub: NlpServiceStub = None
    streaming: bool = False

    @property
    def _llm_type(self) -> str:
        return "caikit_tgis"

    def _call(
        self,
        prompt: str,
        preserve_input_text: bool = False,
        max_new_tokens: int = 512,
        min_new_tokens: int = 10,
        device: str = "",
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        metadata = [("mm-model-id", self.model_id)]
        with open('certificate.pem', 'rb') as f:
            creds = grpc.ssl_channel_credentials(f.read())
        server_address = self.inference_server_url
        channel = grpc.secure_channel(server_address, creds)

        self.nlp_service_stub = NlpServiceStub(channel)

        if self.streaming:
            completion = ""
            for chunk in self._stream(prompt=prompt,
                                      preserve_input_text=preserve_input_text,
                                      max_new_tokens=max_new_tokens,
                                      min_new_tokens=min_new_tokens,
                                      device=device,
                                      stop=stop,
                                      run_manager=run_manager,
                                      **kwargs):
                completion += chunk.text
            return completion

        request = nlpservice_pb2.textgenerationtaskrequest__pb2.TextGenerationTaskRequest(text=prompt,
                                            preserve_input_text=preserve_input_text,
                                            max_new_tokens=max_new_tokens,
                                            min_new_tokens=min_new_tokens)
        response = self.nlp_service_stub.TextGenerationTaskPredict(request=request, metadata=metadata)
        return response.generated_text

    def _stream(
        self,
        prompt: str,
        preserve_input_text: bool = False,
        max_new_tokens: int = 512,
        min_new_tokens: int = 10,
        device: str = "",
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        metadata = [("mm-model-id", self.model_id)]
        request = nlpservice_pb2.textgenerationtaskrequest__pb2.TextGenerationTaskRequest(text=prompt,
                                            preserve_input_text=preserve_input_text,
                                            max_new_tokens=max_new_tokens,
                                            min_new_tokens=min_new_tokens)
        for part in self.nlp_service_stub.ServerStreamingTextGenerationTaskPredict(request=request,metadata=metadata):
            chunk = GenerationChunk(
                text=part.generated_text,
            )
            yield chunk
            if run_manager:
                run_manager.on_llm_new_token(chunk.text)

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"inference_server_url": self.inference_server_url}
