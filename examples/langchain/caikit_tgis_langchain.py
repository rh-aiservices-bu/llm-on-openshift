import sys
sys.path.insert(0, "./pb2")
import nlpservice_pb2_grpc
import nlpservice_pb2
import grpc
from grpc_reflection.v1alpha.proto_reflection_descriptor_database import ProtoReflectionDescriptorDatabase
from google.protobuf.descriptor_pool import DescriptorPool

from typing import Any, List, Mapping, Optional, Iterator
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.pydantic_v1 import Extra, Field, root_validator
from langchain.schema.output import GenerationChunk


class CaikitLLM(LLM):
    inference_server_url: str = ""
    nlp_service_stub: nlpservice_pb2_grpc.NlpServiceStub = None
    streaming: bool = False

    def __init__(self, inference_server_url, streaming):
        super(LLM, self).__init__()
        self.inference_server_url = inference_server_url
        self.nlp_service_stub = self.CreateNlpServiceStub(self.inference_server_url)
        self.streaming = streaming

    def CreateNlpServiceStub(self, inference_server_url):
        with open('certificate.pem', 'rb') as f:
            creds = grpc.ssl_channel_credentials(f.read())
        server_address = inference_server_url
        channel = grpc.secure_channel(server_address, creds)
        NlpServiceStub = nlpservice_pb2_grpc.NlpServiceStub(channel)
        return NlpServiceStub

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
        model_id = 'Llama-2-7b-chat-hf'
        metadata = [("mm-model-id", model_id)]
        if self.streaming:
            print("streaming")
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
        model_id = 'Llama-2-7b-chat-hf'
        metadata = [("mm-model-id", model_id)]
        request = nlpservice_pb2.textgenerationtaskrequest__pb2.TextGenerationTaskRequest(text=prompt,
                                                                                 preserve_input_text=preserve_input_text,
                                                                                 max_new_tokens=max_new_tokens,
                                                                                 min_new_tokens=min_new_tokens)
        for part in self.nlp_service_stub.ServerStreamingTextGenerationTaskPredict(request=request, metadata=metadata):
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
