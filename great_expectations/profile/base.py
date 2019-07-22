import time
import logging

from ..data_asset import DataAsset
from ..dataset import Dataset
from great_expectations.exceptions import GreatExpectationsError

logger = logging.getLogger(__name__)

class DataAssetProfiler(object):

    @classmethod
    def validate(cls, data_asset):
        return isinstance(data_asset, DataAsset)


class DatasetProfiler(object):

    @classmethod
    def validate(cls, dataset):
        return isinstance(dataset, Dataset)

    @classmethod
    def add_expectation_meta(cls, expectation):
        if not "meta" in expectation:
            expectation["meta"] = {}

        expectation["meta"][str(cls.__name__)] = {
            "confidence": "very low"
        }
        return expectation

    @classmethod
    def add_meta(cls, expectation_suite, batch_kwargs=None):
        if not "meta" in expectation_suite:
            expectation_suite["meta"] = {}

        class_name = str(cls.__name__)
        expectation_suite["meta"][class_name] = {
            "created_by": class_name,
            "created_at": time.time(),
        }

        if batch_kwargs is not None:
            expectation_suite["meta"][class_name]["batch_kwargs"] = batch_kwargs

        new_expectations = [cls.add_expectation_meta(
            exp) for exp in expectation_suite["expectations"]]
        expectation_suite["expectations"] = new_expectations

        return expectation_suite

    @classmethod
    def profile(cls, data_asset, run_id=None):
        if not cls.validate(data_asset):
            raise GreatExpectationsError("Invalid data_asset for profiler; aborting")

        expectation_suite = cls._profile(data_asset)

        batch_kwargs = data_asset.get_batch_kwargs()
        expectation_suite = cls.add_meta(expectation_suite, batch_kwargs)
        validation_results = data_asset.validate(expectation_suite, run_id=run_id, result_format="SUMMARY")
        return expectation_suite, validation_results

    @classmethod
    def _profile(cls, dataset):
        raise NotImplementedError