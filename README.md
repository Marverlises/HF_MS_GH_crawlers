# Huggingface, Modelscope, Github 爬虫 —— 使用selenium爬取数据

> [!NOTE]
>
> 本代码仅供学习交流使用

> [!TIP]
>
> 本代码依赖于organization_links文件夹下的相关链接作为起始链接，也可自定义链接地址，根据自己需求自行修改
> 注意在运行之前先查看utils.py文件中17行的os.environ['ALL_PROXY']设置部分，根据自己的设置进行修改

## Huggingface 爬虫 —— Huggingface_crawler

- 如果需要面板的详细信息需要先运行utils_get_huggingface_cookie.py获取cookie
- 本爬虫是基于组织机构的爬虫，爬取的是某个组织下的所有数据集信息
- 运行程序会首先湖片区所有需要的链接存储在 `hugging_face_organization_datasets_links.json` 文件, 然后再爬取每个数据集的详细信息,
  也可以根据需求自定义需要爬取的hf页面链接，基本相同

**示例数据**

```json
{
  "OpenGVLab": {
    "ShareGPT-4o": {
      "dataset_tags_info": {
        "Tasks": "Visual Question Answering Question Answering",
        "Modalities": "Tabular Text",
        "Formats": "json",
        "Languages": "English",
        "Size": "10K - 100K",
        "Libraries": "Datasets pandas Croissant + 1",
        "License": "mit"
      },
      "download_count_last_month": "13,119",
      "link": "https://huggingface.co/datasets/OpenGVLab/ShareGPT-4o",
      "dataset_info": {
        "Size of the auto-converted Parquet files:": "94.2 MB",
        "Number of rows:": "59,400"
      },
      "community": "9",
      "related_models_collections": {
        "Models trained or fine-tuned on OpenGVLab/ShareGPT-4o": {
          "macadeliccc/ShareGPT-4o-MiniCPM-Llama-3-V-2_5": {
            "href": "/macadeliccc/ShareGPT-4o-MiniCPM-Llama-3-V-2_5",
            "text": "Feature Extraction • Updated Jun 17 • 13 • 1"
          },
          "SkyXIntl/SkyReach_Companion_AI": {
            "href": "/SkyXIntl/SkyReach_Companion_AI",
            "text": "Updated Jul 24 • 3"
          },
          "T-ZERO/first_prototype": {
            "href": "/T-ZERO/first_prototype",
            "text": "Text Generation • Updated Jun 16"
          },
          "2024myai/myaitest": {
            "href": "/2024myai/myaitest",
            "text": "Text Classification • Updated Jun 16"
          },
          "hatimismyname/GEn2.0": {
            "href": "/hatimismyname/GEn2.0",
            "text": "Updated Jun 16"
          },
          "knowingpearl/RRATheReactRespondAlgorithm": {
            "href": "/knowingpearl/RRATheReactRespondAlgorithm",
            "text": "Question Answering • Updated Jun 16"
          },
          "expand": {
            "other": "Browse 21 models trained on this dataset"
          }
        }
      },
      "paper_screenshot_save_path": "result/huggingface/hugging_face_dataset_info_screenshots/ShareGPT-4o_pdf.png",
      "dataset_screenshot_save_path": "result/huggingface/hugging_face_dataset_info_screenshots/ShareGPT-4o.png"
    },
    "OmniCorpus-CC": {
      "dataset_tags_info": {
        "Tasks": "Image-to-Text Visual Question Answering",
        "Modalities": "Text",
        "Formats": "parquet",
        "Languages": "English",
        "Size": "100M - 1B",
        "ArXiv": "2406.08418",
        "Libraries": "Datasets Dask Croissant + 1",
        "License": "cc-by-4.0"
      },
      "download_count_last_month": "11,378",
      "link": "https://huggingface.co/datasets/OpenGVLab/OmniCorpus-CC",
      "dataset_info": {
        "Size of downloaded dataset files:": "2.9 TB",
        "Size of the auto-converted Parquet files:": "2.9 TB",
        "Number of rows:": "985,514,699"
      },
      "community": "1",
      "dataset_panel_info": "⭐️ NOTE: Several parquet files were marked unsafe (viruses) by official scaning of hf, while they are reported safe by ClamAV and Virustotal.\nWe found many false positive cases of the hf automatic scanning in ........",
      "related_models_collections": {
        "Collection including OpenGVLab/OmniCorpus-CC": {
          "OmniCorpus Collection": {
            "other": "OmniCorpus Collection OmniCorpus: A Unified Multimodal Corpus of 10 Billion-Level Images Interleaved with Text • 6 items • Updated 23 days ago • 1"
          }
        }
      },
      "paper_screenshot_save_path": "result/huggingface/hugging_face_dataset_info_screenshots/OmniCorpus-CC_pdf.png",
      "dataset_screenshot_save_path": "result/huggingface/hugging_face_dataset_info_screenshots/OmniCorpus-CC.png",
      "modality": "多模态",
      "life_circle": "多模态预训练"
    }
  }
}
```

## Modelscope 爬虫 —— Modelscope_crawler

- 本爬虫是基于组织机构的爬虫，爬取的是某个组织下的所有数据集信息
- 同huggingface爬虫一样，运行程序会首先获取所有需要的链接存储在 `model_scope_organization_datasets_links.json` 文件, 然后再爬取每个数据集的详细信息,
  也可以根据需求自定义需要爬取的modelscope页面链接，基本相同

**数据**

```json
{
  "OpenGVLab": {
    "InternVid": {
      "dataset_license": "cc-by-nc-sa-4.0",
      "related_info": {
        "downloads": 2282,
        "size": "7.90GB",
        "last_update": "2024-10-12"
      },
      "introduction": "InternVid\nDataset Description\nHomepage: InternVid\nRepository: OpenGVLab\nPaper: 2307.06942\nPoint of Contact: mailto:InternVideo\nInternVid-10M-FLT\nWe present InternVid-10M-FLT, a subset of this dataset, consisting of 10 million video clips, with generated high-quality captions for publicly available web videos.\nDownload\nThe 10M samples are provided in jsonlines file. Columns include the videoID, timestamps ......",
      "community_activities": "活跃中（0）\n已完结（0）",
      "dataset_screenshot_save_path": "result/modelscope/model_scope_dataset_info_screenshots/InternVid.png",
      "paper_screenshot_save_path": "result/modelscope/model_scope_dataset_info_screenshots/InternVid_pdf.png",
      "download_num": "2.3k",
      "like_num": "0",
      "last_update_time": "2024.10.12",
      "link": "https://modelscope.cn/datasets/OpenGVLab/InternVid"
    },
    "MMT-Bench": {
      "dataset_license": "cc-by-4.0",
      "related_info": {
        "downloads": 1722,
        "size": "356.51KB",
        "last_update": "2024-07-27"
      },
      "introduction": "该数据集内容暂未更新，敬请期待",
      "community_activities": "活跃中（1）\n已完结（0）",
      "dataset_screenshot_save_path": "result/modelscope/model_scope_dataset_info_screenshots/MMT-Bench.png",
      "paper_screenshot_save_path": "",
      "download_num": "1.7k",
      "like_num": "1",
      "last_update_time": "2024.07.27",
      "link": "https://modelscope.cn/datasets/OpenGVLab/MMT-Bench"
    }
  }
}
```

## Github 爬虫 —— Github_crawler

- 自定义链接爬取github上的数据集信息

**爬取信息示例**
    
```json
       "https://github.com/google/flax": {
        "star_watch_fork": [
            "Notifications You must be signed in to change notification settings",
            "Fork 648",
            "Star 6.1k"
        ],
        "sidebar_data": {
            "Topics": "jax",
            "Resources": "Readme",
            "License": "Apache-2.0 license",
            "Code of conduct": "Code of conduct",
            "Security policy": "Security policy",
            "Stars": "6.1k stars",
            "Watchers": "86 watching",
            "Forks": "648 forks"
        },
        "issues": "Issues\n180",
        "pull_requests": "Pull requests\n127",
        "last_commit": "be26138\n · yesterday\nNov 21, 2024",
        "commits": "History\n4,883 Commits",
        "readme": "Flax: A neural network library and ecosystem for JAX designed for flexibility\nOverview | Quick install | What does Flax look like? | Documentation\nReleased in ......"
    }
}
```
