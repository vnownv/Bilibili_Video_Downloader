#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import progressbar

Bilibili_API = {
    "player_playurl": 'https://api.bilibili.com/x/player/playurl',
    "web_interface_view_detail": 'https://api.bilibili.com/x/web-interface/view/detail'
}

player_playurl_params = {
    "bvid": 'fuck',
    "cid": 0,
    "fnval": 80
}

web_interface_view_detail_params = {
    "bvid": 'fuck'
}

bilibili_headers = {
    "referer": "https://www.bilibili.com",
    "user-agent": 'Safari/537.36'
}

bilibili_cookies = {"SESSDATA": 'FILLIT'}


def get_cid_by_bvid(bvid) -> int:
    web_interface_view_detail_params['bvid'] = bvid
    json = requests.get(url=Bilibili_API['web_interface_view_detail'],
                        params=web_interface_view_detail_params,
                        cookies=bilibili_cookies).json()
    return 1 if json['code'] else json['data']['View']['cid']


def download_video_by_bvid(bvid) -> int:
    cid = get_cid_by_bvid(bvid)
    if cid == 1:
        print("[ERROR] Unable to get cid")
        return 1

    player_playurl_params['bvid'] = bvid
    player_playurl_params['cid'] = cid

    json = requests.get(url=Bilibili_API['player_playurl'],
                        params=player_playurl_params,
                        cookies=bilibili_cookies).json()

    if json['code']:
        print("[ERROR] request player_playurl: " + json['message'])
        return 1

    video_url = json['data']['dash']['video'][0]['baseUrl']
    audio_url = json['data']['dash']['audio'][0]['baseUrl']

    print("[N] Start download...")
    download_url_with_progressbar(video_url, bilibili_headers, 'video' + str(cid))
    download_url_with_progressbar(audio_url, bilibili_headers, 'audio' + str(cid))
    print("[N] Download completed...")

    return 0


def download_url_with_progressbar(url, headers, save_path):
    res = requests.request("GET", url=url, stream=True, headers=headers)
    file_size = int(res.headers.get("Content-Length"))
    with open(save_path, 'wb') as f:
        widgets = ['{} ({:.2f} MB): '.format(save_path, file_size / 1024 / 1024),
                   progressbar.Percentage(), ' ',
                   progressbar.Bar(marker='#', left='[', right=']'), ' ',
                   progressbar.ETA(), ' ',
                   progressbar.FileTransferSpeed()]
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=file_size).start()
        received_size = 0
        for chunk in res.iter_content(chunk_size=1024 * 50):
            if chunk:
                f.write(chunk)
                f.flush()
                received_size += len(chunk)
            pbar.update(received_size)
        pbar.finish()
    return


def main() -> int:
    video_bvid = input('请输入视频 BVID: ')
    return download_video_by_bvid(video_bvid)


if __name__ == '__main__':
    quit(main())
