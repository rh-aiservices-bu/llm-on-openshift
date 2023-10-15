
import grpc
from grpc_reflection.v1alpha.proto_reflection_descriptor_database import ProtoReflectionDescriptorDatabase
from google.protobuf.descriptor_pool import DescriptorPool
from google.protobuf.message_factory import GetMessageClass
from typing import Any, List, Mapping, Optional, Iterator
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.schema.output import GenerationChunk


class CaikitTgisTextGeneration(object):
    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        reflection_db = ProtoReflectionDescriptorDatabase(channel)
        desc_pool = DescriptorPool(reflection_db)
        self.TextGenerationTaskRequest = GetMessageClass(desc_pool.FindMessageTypeByName('caikit.runtime.Nlp.TextGenerationTaskRequest'))()
        self.GeneratedTextResult = GetMessageClass(desc_pool.FindMessageTypeByName('caikit_data_model.nlp.GeneratedTextResult'))()
        self.TextGenerationTaskPredict = channel.unary_unary(
                '/caikit.runtime.Nlp.NlpService/TextGenerationTaskPredict',
                request_serializer=self.TextGenerationTaskRequest.SerializeToString,
                response_deserializer=self.GeneratedTextResult.FromString,
                )
        self.ServerStreamingTextGenerationTaskPredict = channel.unary_stream(
                '/caikit.runtime.Nlp.NlpService/ServerStreamingTextGenerationTaskPredict',
                request_serializer=self.TextGenerationTaskRequest.SerializeToString,
                response_deserializer=self.GeneratedTextResult.FromString,
                )


class CaikitLLM(LLM):
    inference_server_url: str
    model_id: str
    certificate_chain: str = ""
    streaming: bool = False
    caikit_tgis_text_generation_stub: CaikitTgisTextGeneration = None

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
        if self.certificate_chain != "":
            with open(self.certificate_chain, 'rb') as f:
                creds = grpc.ssl_channel_credentials(f.read())
        else:
            creds = None
        server_address = self.inference_server_url
        channel = grpc.secure_channel(server_address, creds)

        self.caikit_tgis_text_generation_stub = CaikitTgisTextGeneration(channel)

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

        request = self.caikit_tgis_text_generation_stub.TextGenerationTaskRequest
        request.text = prompt
        request.preserve_input_text = preserve_input_text
        request.max_new_tokens = max_new_tokens
        request.min_new_tokens = min_new_tokens

        metadata = [("mm-model-id", self.model_id)]

        response = self.caikit_tgis_text_generation_stub.TextGenerationTaskPredict(
            request=request,
            metadata=metadata
        )
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
        request = self.caikit_tgis_text_generation_stub.TextGenerationTaskRequest
        request.text = prompt
        request.preserve_input_text = preserve_input_text
        request.max_new_tokens = max_new_tokens
        request.min_new_tokens = min_new_tokens

        metadata = [("mm-model-id", self.model_id)]

        for part in self.caikit_tgis_text_generation_stub.ServerStreamingTextGenerationTaskPredict(request=request,metadata=metadata):
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
