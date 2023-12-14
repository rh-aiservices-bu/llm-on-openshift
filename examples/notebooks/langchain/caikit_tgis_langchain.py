from typing import Any, Iterator, List, Mapping, Optional, Union
from warnings import warn

from caikit_nlp_client import GrpcClient, HttpClient

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.schema.output import GenerationChunk


class CaikitLLM(LLM):
    def __init__(
        self,
        inference_server_url: str,
        model_id: str,
        certificate_chain: Optional[str] = None,
        streaming: bool = False,
    ):
        super().__init__()

        self.inference_server = inference_server_url
        self.model_id = model_id

        if certificate_chain:
            with open(certificate_chain, "rb") as fh:
                chain = fh.read()
        else:
            chain = None

        if inference_server_url.startswith("http"):
            client = HttpClient(inference_server_url, ca_cert=chain)
        else:
            try:
                host, port = inference_server_url.split(":")
                if not all((host, port)):
                    raise ValueError
            except ValueError:
                raise ValueError(
                    "Invalid url provided, must be either "
                    '"host:port" or "http[s]://host:port/path"'
                )

            client = GrpcClient(host, port, ca_cert=chain)

        self.client: Union[HttpClient, GrpcClient] = client

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
        if self.streaming:
            return "".join(
                self._stream(
                    prompt=prompt,
                    preserve_input_text=preserve_input_text,
                    max_new_tokens=max_new_tokens,
                    min_new_tokens=min_new_tokens,
                    device=device,
                    stop=stop,
                    run_manager=run_manager,
                    **kwargs,
                )
            )
        if run_manager:
            warn("run_manager is ignored for non-streaming use cases")

        if device or stop:
            raise NotImplementedError()

        return self.client.generate_text(
            self.model_id,
            prompt,
            preserve_input_text=preserve_input_text,
            max_new_tokens=max_new_tokens,
            min_new_tokens=min_new_tokens,
        )

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
        if device or stop:
            raise NotImplementedError

        for token in self.client.generate_text_stream(
            self.model_id,
            prompt,
            preserve_input_text=preserve_input_text,
            max_new_tokens=max_new_tokens,
            min_new_tokens=min_new_tokens,
        ):
            chunk = GenerationChunk(text=token)
            yield chunk

            if run_manager:
                run_manager.on_llm_new_token(chunk.text)

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"inference_server_url": self.inference_server_url}
