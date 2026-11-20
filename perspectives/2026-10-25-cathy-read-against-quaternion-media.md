# cathy read against quaternion.media — 2026-10-25

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-25 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

On 2026-10-25 cathy's importer was reviewed against the two records it
implements, then run against quaternion.media, a site Squarespace serves. The
review read `evolve/read-an-export` at `d559602`, quaternionmedia/cathy#2.
The site's own export needs its owner's Squarespace sign-in, which no session
holds and cathy never will. So the run read a stand-in built from the site's
public feeds. To tell cathy's behaviour apart from the stand-in's, it also read
a real export: the one committed in `mrharpo/harpo.me`, whose scripts cathy
generalises. This page is what the run showed, which findings a real export
confirms, and what the records and the run suggest doing next.

## Where the work stood

- quaternionmedia/cathy#1, the adoption, is ready against `main` with every
  check green. quaternionmedia/cathy#2, the importer, is a draft stacked on it.
  `check_one_pr.py` reports the stack as well formed.
- The two records are open in the corpus. quaternionmedia/qm#246, the adoption
  and scope record, is ready against `project/cathy`. quaternionmedia/qm#247,
  the network record, is a draft stacked on it. Both carry *Pends on: Nothing —
  ready for ratification*. quaternionmedia/qm#248, cathy in the roster, and
  quaternionmedia/qm#250, the HTTPS pin check, are ready against `main`. Every
  check on all four is green.
- `uv run pytest tests walkthrough -q`: 63 passed.
  `run_workflows_locally.py --event pull_request --base-ref evolve/adopt-the-corpus --head-ref evolve/read-an-export`:
  all 12 executed steps passed. Leak check and timeless text do not trigger on
  that base.

Nothing in the stack waits on code. It waits on two ratifications, after which
the pin in #1 moves to `project/cathy`'s tip and the stack lands from the
bottom.

## The code against its records

Read against the adoption record's §2 to §4 and the network record's six
points, the importer does what they say. Conversion opens no connection.
`cathy/net.py` is the one module that does: a GET carrying a cathy
`User-Agent` and nothing else, each redirect checked before it is followed,
under a timeout and a size limit. A download lands beside its target and is
renamed into place, and any failed row makes `cathy fetch` exit 1. An export's
author block, comments and attachments are never parsed. A draft needs
`include_drafts`, and a private post is never written.

One property neither the record nor its guard states.
`urllib.request.build_opener` installs a `ProxyHandler` by default, so an
`HTTPS_PROXY` in the environment routes every request through a host that
`cathy.toml` does not name. The request's target is still the named host,
tunnelled. Whether a proxy the person running cathy configured counts as "a
host the site names" is the record's to say. `ProxyHandler({})` removes the
question if the answer is no.

## The run

**The stand-in.** Each of the site's three dated collections, `/projects`,
`/blog` and `/calendar`, has an RSS feed at `?format=rss`. Each of its 46
standalone pages answers `?format=json` with its rendered body. Those 77 bodies
were written into the fields `cathy/wxr.py` reads, every item `publish`. What
the stand-in cannot stand in for:

- A feed holds at most 20 items, and the sitemap lists 24 project posts.
- A public feed holds no drafts or private posts, so §3's selection is not
  exercised.
- Dates are the feed's UTC `pubDate`, not the export's local `post_date`.
- The HTML is what the public pages serve. The next section shows that is not
  what an export holds.

A `cathy.toml` named `/projects/` as the posts collection, listed the 46 pages,
and named `images.squarespace-cdn.com` as the one image host:

```
cathy convert   pages=66 images=103            exit 0
cathy fetch     saved=103 present=0 failed=0   exit 0   59 MB, about 40 s
cathy fetch     saved=0 present=103 failed=0   exit 0
```

Every listed image arrived, from the CDN and nowhere else. Each arrived at full
size, because cathy requests the URL without Squarespace's `?format=` query.
The second fetch found all 103 complete and requested nothing. The 66 pages are
the 20 project posts and the 46 pages. The 5 blog posts and 6 calendar posts
were not written, for the first finding below.

**The real export.** harpo.me's export holds 70 items: 31 published posts, 3
drafts, 10 pages and 26 attachments. cathy read it with the tables
`scripts/convert.py` carries, moved into a `cathy.toml`, and wrote 29 pages,
listed 118 images, and exited 0. It wrote 23 video players, and no image lost
its `src`. Two posts harpo.me's site
publishes, `launchchess` and `pre-visualization`, are drafts in that export and
were not written, as §3 says. A site that wants them sets `include_drafts`.

The site's committed pages are no oracle for cathy's. They were edited after
conversion: images moved to the site's own storage, tags written by hand, a
`<!-- more -->` marker added. So the two were not compared byte for byte.

## What the run found

| | Finding | Stand-in | harpo.me's export |
|---|---|---|---|
| 1 | One posts collection per `cathy.toml` | Three collections; 11 posts not written | One collection |
| 2 | The export's tags are not read | 15 tag pages and 2 category pages in the sitemap | 64 `post_tag` and 50 `category` elements |
| 3 | A post's featured image is not carried | 30 of 31 posts have a thumbnail their body does not show | 26 `_thumbnail_id` entries, naming 26 attachments |
| 4 | Links between pages keep the platform's paths, and no map from old path to page is written | 621 site-relative links, 12 absolute links to the site | 4 site-relative links, 2 absolute links to the site |
| 5 | An `http://` image on a named host is listed but never fetched | None present | None present |
| 6 | An image with only `data-src`, and a video inside Squarespace's `data-html`, are dropped | 183 empty images in 15 pages; 0 of 8 YouTube videos written | Every image has `src`; 29 of 32 iframes are the `embedly-embed` iframe itself, none inside `data-html` |
| 7 | Configured hosts are compared with case | — | — |

**1. One posts collection.** `[posts]` takes one `link_prefix` and one `dir`.
Running cathy once per collection into one docs directory is not safe. Each run
names images against its own URLs only, so two runs can give two different
images the same file name. The second `cathy fetch` then reports that file
`present` and keeps the first image. Several collections in one `cathy.toml`,
named in one run, closes both gaps.

**2. Tags.** cathy takes tags only from `[posts.tags]`, written by hand per
slug, while the export carries the site's own. A post's `category` elements are
fields a page is made from, and the site already publishes them as tag pages,
so reading them sits inside §3 as written. Making it the site's choice keeps
the hand-picked set harpo.me uses.

**3. Featured images.** Squarespace links a post's thumbnail through a
`_thumbnail_id` naming an attachment, and §3 keeps attachments unparsed. On a
portfolio collection the thumbnail is often the post's only image: 19 of the 20
project posts in the stand-in have one their body does not show. Reading an
attachment's `attachment_url` and nothing else would carry it. That changes
what §3 says, so the record is amended before the code.

**4. Links.** A post moves from `/projects/2020/4/19/radio` to
`projects/radio.md`, and nothing records the move. Links between pages keep the
platform's paths, and links from elsewhere to the old URLs break when the site
moves. cathy knows both ends of every page it writes, so it can write the map,
and rewrite a link whose target it wrote.

**5. `http://` images.** Conversion matches `https?://` on a named host and
rewrites the link to a local file. `cathy fetch` permits HTTPS only, so that
row fails on every run and `cathy fetch` exits 1 on every run. This was shown
by editing one fixture URL to `http://`: the page links
`../assets/stage-2bd737c5.jpg`, and fetch refuses the row by its scheme.
Neither corpus holds such a URL, so it is latent. Conversion and fetch should
agree, either by listing HTTPS only or by requesting the HTTPS form of an HTTP
URL on a named host.

**6. Lazy images and video blocks.** The public pages load images lazily, with
the URL in `data-src` and no `src`. They carry a video block's iframe
HTML-escaped inside a `data-html` attribute. Neither reaches a page.
harpo.me's export has neither shape. Every one of its 164 images has a `src`,
and 29 of its 32 iframes are the `embedly-embed` iframe itself, the same iframe
quaternion.media's pages escape inside `data-html`. That reads as the export
unwrapping what the public page wraps, so this is the stand-in's shape and not
an export's. The other reading is that harpo.me's site uses blocks
quaternion.media's does not, and the real export, step 4 below, settles which.
Either way it matters once a source reads public pages, the adoption record's
third alternative.

**7. Host case.** `urlsplit` lowercases a URL's host, and a `cathy.toml` host
is compared as written, so `Images.Squarespace-CDN.com` refuses every row.
Lowercasing configured hosts at load closes it.

## Next steps, against what the records advise

**What the records and `AGENTS.md` already name.**

1. Ratify quaternionmedia/qm#246, then quaternionmedia/qm#247. Both are a
   person's act. Then move the pin in quaternionmedia/cathy#1 to
   `project/cathy`'s tip, so the record paths `AGENTS.md` names resolve. Land
   #1, retarget #2 onto `main`, mark it ready, and land it.
2. Land quaternionmedia/qm#248 and quaternionmedia/qm#250, which do not depend
   on the stack.
3. Meet the adoption record's obligations, none of which is met yet: the
   licence gate for the Python ecosystem, the risk register, the quarterly
   upstream scan, and tag claims at the first `v*` tag. The locked runtime
   closure is still the five packages the record names. The licence gate comes
   first, since the first tag runs it.

**What the run adds**, in the order the run suggests.

4. Read quaternion.media's real export once. Its owner downloads the WordPress
   export from the site's Squarespace settings, and cathy reads it in a
   directory that belongs to the site, never in cathy's repository (§3). It
   settles which of findings 1 to 5 the site has, and how many posts the
   stand-in's 20-item feed hid.
5. Several posts collections in one `cathy.toml` (finding 1). It is the
   smallest change that lets cathy read quaternion.media whole.
6. Conversion and fetch agree on schemes, and configured hosts are lowercased
   (findings 5 and 7). Each is a few lines and a test.
7. Tags from the export, as the site's choice (finding 2).
8. An amendment to §3 for an attachment's URL, then featured images
   (finding 3).
9. A path map and link rewriting (finding 4).
10. A public-page source, under its own record and its own §3 check, when a
    site without an export needs one (finding 6).
