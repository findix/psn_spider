#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Spider of PlayStation Store, read by API"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from datetime import datetime

import requests

from game_info import GameInfo, get_session


def get_data(session, url, payload):
    r = requests.get(url, params=payload)
    json = r.json()
    for i, e in enumerate(json["links"]):
        game = GameInfo(
            cid=e["id"],
            name=e["name"],
            genre=",".join(e["metadata"]["genre"]["values"]
                           ) if "genre" in e["metadata"] else None,
            content_type=e["gameContentTypesList"][0]["name"] if "gameContentTypesList" in e else None,
            provider=e["provider_name"] if "provider_name" in e else None,
            release_date=datetime.strptime(
                e["release_date"], r"%Y-%m-%dT%H:%M:%SZ").date() if "release_date" in e else None,
            num_of_reviews=e["star_rating"]["total"],
            price=e["default_sku"]["price"] if "default_sku" in e else None,
            url=e["url"],
            update_datetime=datetime.now(),
        )
        if session.query(GameInfo).filter(GameInfo.cid == game.cid).first() is None:
            session.add(game)
            # print(i, game.name)
        else:
            print(i, game.name, "is exist in the database")


def main():
    """ Main"""
    session = get_session("psn_us")

    us_all_url = r'https://store.playstation.com/chihiro-api/viewfinder/US/en/999/STORE-MSF77008-PS4ALLGAMESCATEG'
    us_all_payload = {
        "platform": "ps4",
        "game_content_type": "games",
        "start": 0,
        "size": 2000,
        "geoCountry": "CN",
        "gbk": 1
    }
    get_data(session, us_all_url, us_all_payload)

    us_indie_url = r'https://store.playstation.com/chihiro-api/viewfinder/US/en/999/STORE-MSF77008-PS4INDIESGAMECAT'
    us_indie_payload = {
        "platform": "ps4",
        "start": 0,
        "size": 2000,
        "geoCountry": "CN",
        "gbk": 1
    }

    get_data(session, us_indie_url, us_indie_payload)

    session.commit()

    session = get_session("psn_hk")

    hk_url = r"https://store.playstation.com/chihiro-api/viewfinder/HK/zh/19/STORE-MSF86012-PS4TITLES"

    hk_payload = {
        "platform": "ps4",
        "game_content_type": "games",
        "start": 0,
        "size": 2000,
        "geoCountry": "CN",
        "gbk": 1
    }
    get_data(session, hk_url, hk_payload)

    session.commit()


if __name__ == '__main__':
    main()
