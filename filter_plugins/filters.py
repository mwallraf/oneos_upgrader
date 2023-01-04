#!/usr/bin/python

import re
import math


class FilterModule(object):
    """Nested dict filter"""

    def filters(self):
        return {
            "normalize_memory": self.normalize_memory,
        }
        
    def _convert_unit(self, data, have_unit, want_unit):
        """converts integer data from one unit to another
        """
        newdata = data
        
        unit_map = {
            "g": "gb",
            "m": "mb",
            "k": "kb",
            "b": "b",
            "kb": "kb",
            "mb": "mb",
            "gb": "gb",
        }
        
        # convert original data to bytes
        if unit_map[have_unit.lower()] == "kb":
            newdata = data * 1024
        elif unit_map[have_unit.lower()] == "mb":
            newdata = data * 1024 * 1024
        elif unit_map[have_unit.lower()] == "gb":
            newdata = data * 1024 * 1024 * 1024
            
        if want_unit == "kb":
            newdata = newdata / 1024
        elif want_unit == "mb":
            newdata = newdata / 1024 / 1024
        elif want_unit == "gb":
            newdata = newdata / 1024 / 1024 / 1024
        
        return math.ceil(newdata)
            

    def normalize_memory(self, data, unit="kb"):
        """Normalizes the output of "show memory" and converts
        everything into the requested unit.
        
        The field USER_PARTITION_USED may have a percentage and this will
        be converted to the actual value. 

        unit = b (bytes), kb (kbytes), mb (megabytes), gb (gigabytes)

        Example data:
                        "BOOT_SIZE": "100.0MiB",
                        "FLASH_SIZE": "512.0MiB",
                        "RAM": "1.0GiB",
                        "USER_PARTITION_FREE": "85.4MiB",
                        "USER_PARTITION_TOTAL": "366.9MiB",
                        "USER_PARTITION_USED": "76.7%"

                        "BOOT_SIZE": "1 024",
                        "FLASH_SIZE": "65 536",
                        "RAM": "262 144",
                        "USER_PARTITION_FREE": "33 512",
                        "USER_PARTITION_TOTAL": "64 688",
                        "USER_PARTITION_USED": "31 176"
        """
        re_kb = re.compile(r"^\d+\s\d+")
        re_unit = re.compile(r"^(?P<VAL>\d+(\.\d+)?)(?P<UNIT>[MGK])iB")

        result = {}

        for k_key, k_value in data.items():
            # standard oneos 5 kilobytes format
            if re_kb.match(k_value):
                result[k_key] = eval(k_value.replace(" ", ""))
                result[k_key] = self._convert_unit(result[k_key], "kb", unit)
            # oneos 6 format with the unit included
            elif re_unit.match(k_value):
                m = re_unit.match(k_value)
                result[k_key] = eval(m.groupdict()["VAL"])
                result[k_key] = self._convert_unit(result[k_key], m.groupdict()["UNIT"], unit)
            else:
                result[k_key] = k_value

        # if percentage exist for USER_PARTITION_USED then calculate the actual value if possible
        if type(result.get("USER_PARTITION_USED", "")) is str and "%" in result.get(
            "USER_PARTITION_USED", ""
        ):
            if (
                type(result.get("USER_PARTITION_TOTAL", "")) is not str
                and type(result.get("USER_PARTITION_FREE", "")) is not str
            ):
                result["USER_PARTITION_USED"] = (
                    result["USER_PARTITION_TOTAL"] - result["USER_PARTITION_FREE"]
                )

        return result
