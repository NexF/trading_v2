import tframe.tframe as tframe


class TContextFactory:
    # tcontext字典
    __tcontext_dict: dict = {}

    # 注册tcontext
    @staticmethod
    def register_tcontext(
        tcontext_name: str, tcontext_session: type, tcontext_strategyinfo: type
    ):
        TContextFactory.__tcontext_dict[tcontext_name] = (
            tcontext_session,
            tcontext_strategyinfo,
        )

    @staticmethod
    def create_tcontext(tcontext_name: str) -> tframe.TContext:
        tcontext_session, tcontext_strategyinfo = TContextFactory.__tcontext_dict[
            tcontext_name
        ]
        return tframe.TContext(tcontext_session, tcontext_strategyinfo)
