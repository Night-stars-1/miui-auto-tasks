"""
Date: 2023-11-13 19:55:22
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2025-02-14 18:46:15
"""

import json
import time
from traceback import print_exc

from jsonpath_ng import parse
from jsonpath_ng.exceptions import JsonPathParserError

from .config import ConfigManager
from .data_model import GeetestResult
from .logger import log
from .request import request

_conf = ConfigManager.data_obj


def get_value_by_jsonpath(data: dict, jsonpath: str):
    """
    根据jsonpath获取value
    :return: 如果未找到则返回空字符
    """
    result = ""
    try:
        geetest_validate_expr = parse(jsonpath)
        geetest_validate_match = geetest_validate_expr.find(data)
        if len(geetest_validate_match) > 0:
            result: str = geetest_validate_match[0].value
    except JsonPathParserError:
        print_exc()
    return result


def get_validate_other(
    gt: str, challenge: str, result: str, url: str
) -> GeetestResult:  # pylint: disable=invalid-name
    """获取人机验证结果"""
    try:
        validate = ""
        if _conf.preference.get_geetest_url:
            params = _conf.preference.get_geetest_params.copy()
            params = json.loads(
                json.dumps(params)
                .replace("{gt}", gt)
                .replace("{challenge}", challenge)
                .replace("{result}", str(result))
                .replace("{url}", url)
            )
            data = _conf.preference.get_geetest_data.copy()
            data = json.loads(
                json.dumps(data)
                .replace("{gt}", gt)
                .replace("{challenge}", challenge)
                .replace("{result}", str(result))
                .replace("{url}", url)
            )
            for i in range(_conf.preference.get_geetest_try_count):
                log.info(f"第{i}次获取结果")
                response = request(
                    _conf.preference.get_geetest_method,
                    _conf.preference.get_geetest_url,
                    params=params,
                    json=data,
                )
                log.debug(response.text)
                result = response.json()
                validate = get_value_by_jsonpath(
                    result, _conf.preference.get_geetest_validate_path
                )
                challenge = get_value_by_jsonpath(
                    result, _conf.preference.get_geetest_challenge_path
                )
                if validate and challenge:
                    return GeetestResult(challenge=challenge, validate=validate)
                time.sleep(1)
            return GeetestResult(challenge="", validate="")
        else:
            return GeetestResult(challenge="", validate="")
    except Exception:  # pylint: disable=broad-exception-caught
        log.exception("获取人机验证结果异常")
        return GeetestResult(challenge="", validate="")


def get_validate(
    gt: str, challenge: str, url: str
) -> GeetestResult:  # pylint: disable=invalid-name
    """创建人机验证并结果"""
    try:
        validate = ""
        result = ""
        if _conf.preference.geetest_url:
            params = _conf.preference.geetest_params.copy()
            params = json.loads(
                json.dumps(params)
                .replace("{gt}", gt)
                .replace("{challenge}", challenge)
                .replace("{url}", url)
            )
            data = _conf.preference.geetest_data.copy()
            data = json.loads(
                json.dumps(data)
                .replace("{gt}", gt)
                .replace("{challenge}", challenge)
                .replace("{url}", url)
            )
            response = request(
                _conf.preference.geetest_method,
                _conf.preference.geetest_url,
                params=params,
                json=data,
            )
            log.debug(response.text)
            result = response.json()
            validate = get_value_by_jsonpath(
                result, _conf.preference.geetest_validate_path
            )
            challenge = get_value_by_jsonpath(
                result, _conf.preference.geetest_challenge_path
            )
            result = get_value_by_jsonpath(result, _conf.preference.geetest_result_path)
            if validate and challenge:
                return GeetestResult(challenge=challenge, validate=validate)
            else:
                return get_validate_other(
                    gt=gt, challenge=challenge, result=result, url=url
                )
        else:
            return GeetestResult(challenge="", validate="")
    except Exception:  # pylint: disable=broad-exception-caught
        log.exception("获取人机验证结果异常")
        return GeetestResult(challenge="", validate="")
