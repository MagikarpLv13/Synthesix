from __future__ import annotations

import json
from typing import Any, Mapping

import observability


MAX_SOCIAL_BODY_TEXT_LENGTH = 50_000
MAX_SOCIAL_ITEM_LENGTH = 2_000
MAX_SOCIAL_LINKS = 200
MAX_SOCIAL_LABELS = 300
MAX_SOCIAL_JSON_LD_ITEMS = 20
MAX_SOCIAL_JSON_LD_LENGTH = 50_000


async def social_profile_snapshot(
    tab,
    profile: str,
    metrics: list[str] | tuple[str, ...],
    selectors: Mapping[str, str],
) -> Mapping[str, Any]:
    """Collect bounded signals for a versioned social DOM parser.

    The page is inspected in one CDP evaluate. Only metadata, selected
    attributes, bounded visible text, links and JSON-LD snippets are returned;
    full DOM HTML, screenshots and archives are never captured here.
    """
    request = json.dumps(
        {
            "profile": str(profile),
            "metrics": [str(metric) for metric in metrics],
            "selectors": {
                str(metric): str(selector)
                for metric, selector in selectors.items()
            },
            "maxBodyTextLength": MAX_SOCIAL_BODY_TEXT_LENGTH,
            "maxItemLength": MAX_SOCIAL_ITEM_LENGTH,
            "maxLinks": MAX_SOCIAL_LINKS,
            "maxLabels": MAX_SOCIAL_LABELS,
            "maxJsonLdItems": MAX_SOCIAL_JSON_LD_ITEMS,
            "maxJsonLdLength": MAX_SOCIAL_JSON_LD_LENGTH,
        },
        ensure_ascii=False,
    )
    script = r"""
    (() => {
      const request = __SYNTHESIX_SOCIAL_REQUEST__;
      const customMetrics = {};
      const errors = [];
      const collapse = (value, limit = request.maxItemLength) =>
        String(value ?? "").replace(/\s+/g, " ").trim().slice(0, limit);
      const numberValue = (value) => {
        const text = collapse(value);
        if (!text) return null;
        const compact = text.replace(/[\s\u00a0\u202f]/g, "");
        if (!/^[+-]?\d+(?:[.,]\d+)?$/.test(compact)) return null;
        const parsed = Number(compact.replace(",", "."));
        return Number.isFinite(parsed) ? parsed : null;
      };
      const scalarValue = (node) => {
        const raw = collapse(
          node instanceof HTMLInputElement
            || node instanceof HTMLTextAreaElement
            || node instanceof HTMLSelectElement
            ? node.value
            : node.currentSrc
              || node.src
              || node.href?.baseVal
              || node.getAttribute?.("src")
              || node.getAttribute?.("href")
              || node.getAttribute?.("xlink:href")
              || node.getAttribute?.("data-value")
              || node.textContent
        );
        const numeric = numberValue(raw);
        if (numeric !== null) return {kind: "number", value: numeric};
        return {kind: "text", value: raw};
      };
      const selectorMetric = (metric, selector) => {
        try {
          const allNodes = Array.from(document.querySelectorAll(selector));
          const nodes = allNodes.slice(0, request.maxLinks);
          if (!nodes.length) {
            return {status: "missing", kind: "text", value: null};
          }
          const values = nodes.map(scalarValue);
          if (values.length === 1) {
            const value = values[0];
            return {
              status: value.value === "" ? "missing" : "ok",
              kind: value.kind,
              value: value.value === "" ? null : value.value,
            };
          }
          return {
            status: "ok",
            kind: "list",
            value: values.map((item) => item.value),
            truncated: allNodes.length > nodes.length,
          };
        } catch (error) {
          errors.push({
            metric,
            code: "invalid_selector",
            message: collapse(error?.message || error, 500),
          });
          return {status: "error", kind: "text", value: null};
        }
      };
      const isVisible = (node) => {
        if (!(node instanceof Element)) return false;
        const style = getComputedStyle(node);
        const rect = node.getBoundingClientRect();
        return (
          style.display !== "none"
          && style.visibility !== "hidden"
          && Number(style.opacity || 1) !== 0
          && rect.width > 0
          && rect.height > 0
        );
      };
      const directText = (node) => Array.from(node?.childNodes || [])
        .filter((child) => child.nodeType === Node.TEXT_NODE)
        .map((child) => String(child.nodeValue || ""))
        .join("");
      const renderedLeafText = (node) => {
        if (!(node instanceof Element) || !isVisible(node)) return "";
        const container = node.getBoundingClientRect();
        const glyphs = [node, ...node.querySelectorAll("*")]
          .map((element) => ({
            element,
            text: directText(element),
            rect: element.getBoundingClientRect(),
          }))
          .filter(({element, text, rect}) => (
            text
            && (
              isVisible(element)
              || (
                /^\s+$/.test(text)
                && getComputedStyle(element).display !== "none"
                && getComputedStyle(element).visibility !== "hidden"
                && rect.height > 0
              )
            )
            && rect.right >= container.left - 1
            && rect.left <= container.right + 1
            && rect.bottom >= container.top - 1
            && rect.top <= container.bottom + 1
          ))
          .sort((left, right) => (
            Math.abs(left.rect.top - right.rect.top) > 2
              ? left.rect.top - right.rect.top
              : left.rect.left - right.rect.left
          ));
        return collapse(glyphs.map(({text}) => text).join(""), 500);
      };
      const referencedLabel = (node) => {
        const reference = node?.querySelector?.("[aria-labelledby]");
        if (!reference) return "";
        return collapse(
          String(reference.getAttribute("aria-labelledby") || "")
            .split(/\s+/)
            .map((id) => document.getElementById(id)?.innerText || "")
            .join(" "),
          500
        );
      };
      const facebookUrl = (value) => {
        try {
          return new URL(String(value || ""), location.href);
        } catch (_error) {
          return null;
        }
      };
      const facebookPermalink = (value) => {
        const parsed = facebookUrl(value);
        if (!parsed) return "";
        const storyId = parsed.searchParams.get("story_fbid");
        const objectId = parsed.searchParams.get("fbid");
        const ownerId = parsed.searchParams.get("id");
        if (storyId) {
          const suffix = ownerId ? `&id=${encodeURIComponent(ownerId)}` : "";
          return `${parsed.origin}${parsed.pathname}`
            + `?story_fbid=${encodeURIComponent(storyId)}${suffix}`;
        }
        if (objectId) {
          return `${parsed.origin}${parsed.pathname}`
            + `?fbid=${encodeURIComponent(objectId)}`;
        }
        if (/\/(?:posts|videos|reel)\//i.test(parsed.pathname)) {
          return `${parsed.origin}${parsed.pathname}`;
        }
        return "";
      };
      const facebookPostId = (value) => {
        const parsed = facebookUrl(value);
        if (!parsed) return "";
        const queryId = parsed.searchParams.get("story_fbid")
          || parsed.searchParams.get("fbid");
        if (queryId) return collapse(queryId, 500);
        const match = parsed.pathname.match(
          /\/(?:posts|videos|reel)\/([^/?#]+)/i
        );
        return collapse(match?.[1], 500);
      };
      const facebookDateLabel = (...values) => values
        .map((value) => collapse(value, 500))
        .find((value) => (
          value
          && value.length <= 200
          && (
            /\b\d{1,2}:\d{2}\b/.test(value)
            || /\b\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?\b/.test(value)
            || /\b(?:today|yesterday|monday|tuesday|wednesday|thursday|friday|saturday|sunday|hier|aujourd'hui|lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|janv(?:ier)?|févr(?:ier)?|mars|avr(?:il)?|mai|juin|juil(?:let)?|août|sept(?:embre)?|oct(?:obre)?|nov(?:embre)?|déc(?:embre)?|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|hoje|ontem|heute|gestern)\b/i.test(value)
            || /\b\d+\s*(?:s|min|h|j|d|sem|semaine|jour|heure|minute|day|hour|week|month|year|ano|jahr)\b/i.test(value)
            || /(?:今天|昨天|分钟前|小时前|天前|月|日)/.test(value)
          )
        )) || "";
      const facebookPhotoSource = (node) => collapse(
        node?.currentSrc
          || node?.src
          || node?.href?.baseVal
          || node?.getAttribute?.("href")
          || node?.getAttribute?.("xlink:href"),
        4000
      );
      const facebookPhotoIdentity = (value) => {
        const parsed = facebookUrl(value);
        if (!parsed) return "";
        const filename = decodeURIComponent(
          parsed.pathname.split("/").filter(Boolean).pop() || ""
        );
        return collapse(filename || parsed.pathname, 1000);
      };
      const facebookProfileSignals = () => {
        if (request.profile !== "facebook_page") return {};
        const page = facebookUrl(location.href);
        const pageHost = String(page?.hostname || "").toLocaleLowerCase();
        const pageIsFacebook = /(?:^|\.)(?:facebook\.com|fb\.com)$/.test(
          pageHost
        );
        const pageProfileId = pageIsFacebook
          ? page?.searchParams.get("id") || ""
          : "";
        const pageSlug = (pageIsFacebook ? String(page?.pathname || "") : "")
          .split("/")
          .filter(Boolean)[0]
          ?.toLocaleLowerCase() || "";
        const friendLinks = Array.from(
          document.querySelectorAll(
            'a[href*="sk=friends"], a[href*="/friends"]'
          )
        ).filter((node) => {
          const parsed = facebookUrl(node.href);
          const section = parsed?.searchParams.get("sk") || "";
          const candidateId = parsed?.searchParams.get("id") || "";
          const candidateParts = String(parsed?.pathname || "")
            .split("/")
            .filter(Boolean);
          const candidateSlug = candidateParts[0]?.toLocaleLowerCase() || "";
          const isFriendsSection = section.startsWith("friends")
            || candidateParts.some((part) => (
              part.toLocaleLowerCase().startsWith("friends")
            ));
          const sameProfile = pageProfileId
            ? candidateId === pageProfileId
            : pageSlug
              ? pageSlug === candidateSlug
              : Boolean(candidateId || candidateSlug !== "friends");
          return (
            isFriendsSection
            && sameProfile
          );
        });
        const friendsLink = friendLinks
          .map((node) => {
            const parsed = facebookUrl(node.href);
            const text = collapse(node.innerText || node.textContent, 500);
            let score = 0;
            if (isVisible(node)) score += 20;
            if (parsed?.searchParams.get("id")) score += 25;
            if (parsed?.searchParams.get("sk") === "friends_all") score += 30;
            if (/\d/.test(text)) score += 35;
            if (/(?:ami(?:\(e\)|e)?s?|friends?|amigos?|freunde|朋友)/i.test(text)) {
              score += 15;
            }
            return {node, score};
          })
          .sort((left, right) => right.score - left.score)[0]?.node || null;
        const friendsText = collapse(
          friendsLink?.innerText || friendsLink?.textContent,
          500
        );
        const friendsCountText = collapse(
          friendsLink?.querySelector("strong, [data-value]")?.getAttribute?.(
            "data-value"
          )
          || friendsLink?.querySelector("strong, [data-value]")?.innerText
          || friendsText,
          200
        );

        let displayName = "";
        if (friendsLink) {
          let boundary = friendsLink.parentElement;
          const displayCandidates = [];
          for (let depth = 0; boundary && depth < 14; depth += 1) {
            const candidates = Array.from(
              boundary.querySelectorAll(
                'h1, h2, h3, [role="heading"], [role="button"]'
              )
            )
              .filter((node) => !node.contains(friendsLink))
              .map((node) => ({
                node,
                text: collapse(node.innerText || node.textContent, 200),
              }))
              .filter(({node, text}) => (
                text
                && text !== friendsText
                && !text.includes(friendsText)
                && text.length <= 120
                && /[^\d\W]/u.test(text)
                && isVisible(node)
                && !/(?:en commun|mutual|ami(?:\(e\)|e)?s?|friends?|message|follow|suivre|abonn)/i.test(text)
              ))
              .map((candidate) => ({
                ...candidate,
                score: (
                  /^(H1|H2|H3)$/i.test(candidate.node.tagName) ? 100 : 0
                ) + (
                  candidate.node.getAttribute("role") === "heading" ? 80 : 0
                ) + (
                  candidate.node.getAttribute("role") === "button" ? 25 : 0
                ) - depth * 3 - candidate.text.length / 1000,
              }));
            displayCandidates.push(...candidates);
            boundary = boundary.parentElement;
          }
          displayName = displayCandidates.sort(
            (left, right) => right.score - left.score
          )[0]?.text || "";
        }
        if (!displayName) {
          displayName = collapse(
            document.querySelector('main h1, [role="main"] h1, h1')?.innerText,
            200
          );
        }

        let profileRoot = friendsLink?.parentElement || null;
        for (let depth = 0; profileRoot && depth < 18; depth += 1) {
          const hasNamedImage = displayName && Array.from(
            profileRoot.querySelectorAll('[aria-label]')
          ).some((node) => (
            collapse(node.getAttribute("aria-label"), 200) === displayName
            && node.querySelector("img[src], svg image")
          ));
          const hasCover = profileRoot.querySelector(
            '[data-imgperflogname="profileCoverPhoto"], '
            + '[aria-label*="cover photo" i], '
            + '[aria-label*="photo de couverture" i]'
          );
          if (hasNamedImage && hasCover) break;
          profileRoot = profileRoot.parentElement;
        }
        profileRoot ||= document.querySelector('[role="main"], main')
          || document.body;

        const mutualCountPattern = /^(\d[\d\s\u00a0\u202f.,]*(?:\s*(?:k|m|b|bn|mio))?)\s*\(\s*\d[\d\s\u00a0\u202f.,]*\s+(?:en\s+commun|ami(?:\(e\)|e)?s?\s+en\s+commun|mutual\s+friends?|amigos?\s+en\s+com[uú]n|gemeinsame\s+freunde)\s*\)$/i;
        const exactFriendsNode = Array.from(
          document.querySelectorAll("span, div")
        )
          .map((node) => {
            const text = collapse(node.innerText || node.textContent, 200);
            if (!mutualCountPattern.test(text)) return null;
            let ancestor = node.parentElement;
            for (let depth = 0; ancestor && depth < 18; depth += 1) {
              if (friendLinks.some((link) => ancestor.contains(link))) {
                return {node, depth};
              }
              ancestor = ancestor.parentElement;
            }
            return null;
          })
          .filter(Boolean)
          .sort((left, right) => left.depth - right.depth)[0]?.node || null;
        const exactFriendsMatch = collapse(
          exactFriendsNode?.innerText || exactFriendsNode?.textContent,
          200
        ).match(mutualCountPattern);
        const preferredFriendsCountText = collapse(
          exactFriendsMatch?.[1] || friendsCountText,
          200
        );

        const profilePhotoPattern = /(?:profile photo|photo de profil|foto de perfil|foto do perfil|profilbild|头像|大頭貼)/i;
        const photoCandidates = Array.from(
          document.querySelectorAll("img[src], svg image")
        )
          .map((node) => {
            const source = facebookPhotoSource(node);
            const rect = node.getBoundingClientRect();
            const labelNode = node.closest("[aria-label]");
            const label = collapse(labelNode?.getAttribute("aria-label"), 300);
            const perfNode = node.closest("[data-imgperflogname]");
            const perfName = collapse(
              perfNode?.getAttribute("data-imgperflogname"),
              100
            );
            let score = 0;
            if (profilePhotoPattern.test(label)) score += 45;
            if (/profilephoto/i.test(perfName)) score += 120;
            if (/\/t\d+\.\d+-1\//.test(source)) score += 30;
            if (/scontent[^/]*\.xx\.fbcdn\.net/i.test(source)) score += 15;
            if (/static\.xx\.fbcdn\.net/i.test(source)) score -= 100;
            if (rect.width >= 64 && rect.width <= 400) score += 15;
            if (
              rect.width > 0
              && rect.height > 0
              && Math.abs(rect.width - rect.height) / Math.max(
                rect.width,
                rect.height
              ) <= 0.15
            ) score += 20;
            if (displayName && label === displayName) score += 180;
            if (profileRoot?.contains(node)) score += 80;
            if (friendsLink) {
              let ancestor = friendsLink.parentElement;
              for (let depth = 0; ancestor && depth < 14; depth += 1) {
                if (ancestor.contains(node)) {
                  score += Math.max(0, 30 - depth * 2);
                  break;
                }
                ancestor = ancestor.parentElement;
              }
            }
            return {node, source, score, area: rect.width * rect.height};
          })
          .filter(({node, source}) => source && isVisible(node))
          .sort((left, right) => (
            right.score - left.score || right.area - left.area
          ));
        const profilePhotoUrl = photoCandidates[0]?.source || "";
        const coverPhotoNode = profileRoot.querySelector(
          'img[data-imgperflogname="profileCoverPhoto"]'
        ) || Array.from(
          profileRoot.querySelectorAll(
            '[aria-label*="cover photo" i] img[src], '
            + '[aria-label*="photo de couverture" i] img[src]'
          )
        )[0] || null;
        const coverPhotoUrl = facebookPhotoSource(coverPhotoNode);

        const detailHeadingPattern = /^(?:intro|introduction|présentation|about|à propos|personal information|informations personnelles|información personal|informações pessoais|persönliche informationen|education|formation|work and education|emploi et formation|places lived|lieux de résidence|contact and basic info|coordonnées et informations générales|family and relationships|famille et relations|details about|détails sur)$/i;
        const detailSections = [];
        const detailScopes = [];
        Array.from(
          profileRoot.querySelectorAll('h1, h2, h3, [role="heading"]')
        ).forEach((heading) => {
          const title = collapse(heading.innerText || heading.textContent, 120);
          if (!detailHeadingPattern.test(title)) return;
          let scope = heading.parentElement;
          for (let depth = 0; scope && depth < 6; depth += 1) {
            if (scope.querySelector('[role="listitem"]')) break;
            scope = scope.parentElement;
          }
          if (!scope || !scope.querySelector('[role="listitem"]')) return;
          detailScopes.push(scope);
          Array.from(scope.querySelectorAll('[role="listitem"]'))
            .map((node) => collapse(node.innerText || node.textContent, 500))
            .filter((value) => value && value !== title)
            .forEach((value) => detailSections.push(`${title}: ${value}`));
        });
        Array.from(
          profileRoot.querySelectorAll('[role="list"][aria-label]')
        ).filter((node) => (
          /(?:featured details|détails à la une|detalles destacados|destaques|hervorgehobene details)/i.test(
            node.getAttribute("aria-label") || ""
          )
        )).forEach((scope) => {
          detailScopes.push(scope);
          Array.from(scope.querySelectorAll('[role="listitem"]'))
            .map((node) => collapse(node.innerText || node.textContent, 500))
            .filter(Boolean)
            .forEach((value) => detailSections.push(value));
        });
        const profileDetails = Array.from(new Set(detailSections)).slice(0, 50);
        const detailLinks = Array.from(new Set(
          detailScopes.flatMap((scope) => Array.from(
            scope.querySelectorAll("a[href]")
          ).map((node) => collapse(node.href, 4000)))
        )).filter((value) => {
          const parsed = facebookUrl(value);
          const hostname = String(parsed?.hostname || "").toLocaleLowerCase();
          return parsed?.protocol === "https:"
            && !/(?:^|\.)(?:facebook\.com|fb\.com|fbcdn\.net)$/.test(hostname);
        }).slice(0, request.maxLinks);
        const headerText = collapse(profileRoot.innerText, 10_000);
        const followersMatch = headerText.match(
          /(\d[\d\s\u00a0\u202f.,]*(?:\s*(?:k|m|b|bn|mio))?)\s+(?:followers?|abonn[ée]s?|seguidores?|follower|粉丝|粉絲|追蹤者)/i
        );
        const explicitBio = profileRoot.querySelector(
          '[data-testid="profile_intro_card_bio"]'
        );
        const profileBio = collapse(
          explicitBio?.innerText || explicitBio?.textContent,
          2_000
        );

        const postsHeadingPattern = /^(?:posts|publications|publicaciones|publicações|beiträge|帖子)$/i;
        const postsHeading = Array.from(
          document.querySelectorAll('h1, h2, [role="heading"]')
        ).find((node) => postsHeadingPattern.test(
          collapse(node.innerText || node.textContent, 100)
        ));
        let postsScope = postsHeading?.parentElement || null;
        for (let depth = 0; postsScope && depth < 12; depth += 1) {
          if (postsScope.querySelector("[aria-posinset]")) break;
          postsScope = postsScope.parentElement;
        }
        const postRoots = Array.from(
          (postsScope || profileRoot || document).querySelectorAll("[aria-posinset]")
        )
          .filter((node) => (
            node.querySelector(
              '[data-ad-preview="message"], '
              + '[data-ad-comet-preview="message"], '
              + '[data-ad-rendering-role="story_message"], '
              + 'a[href*="story_fbid="], a[href*="/posts/"], '
              + 'a[href] [aria-labelledby]'
            )
          ))
          .sort((left, right) => (
            Number(left.getAttribute("aria-posinset") || 0)
            - Number(right.getAttribute("aria-posinset") || 0)
          ));
        const pinnedPattern = /(?:publication épinglée|épinglé|pinned post|pinned|publicación fijada|fixado|angeheftet)/i;
        const isPinned = (node) => Array.from(
          node.querySelectorAll("[aria-label], [title]")
        ).some((candidate) => pinnedPattern.test(
          `${candidate.getAttribute("aria-label") || ""} `
          + `${candidate.getAttribute("title") || ""}`
        ));
        const post = postRoots.find((node) => !isPinned(node))
          || postRoots[0]
          || null;
        const messageNode = post?.querySelector(
          '[data-ad-preview="message"], '
          + '[data-ad-comet-preview="message"], '
          + '[data-ad-rendering-role="story_message"]'
        );
        let messageRaw = String(
          messageNode?.innerText || messageNode?.textContent || ""
        ).replace(/\s+/g, " ").trim();
        if (
          messageRaw.length % 2 === 0
          && messageRaw.slice(0, messageRaw.length / 2)
            === messageRaw.slice(messageRaw.length / 2)
        ) {
          messageRaw = messageRaw.slice(0, messageRaw.length / 2);
        } else if (messageRaw.length % 2 === 1) {
          const midpoint = Math.floor(messageRaw.length / 2);
          if (
            messageRaw[midpoint] === " "
            && messageRaw.slice(0, midpoint)
              === messageRaw.slice(midpoint + 1)
          ) {
            messageRaw = messageRaw.slice(0, midpoint);
          }
        }
        const dateReference = post?.querySelector(
          'a[href] > span[aria-labelledby], a[href] [aria-labelledby]'
        );
        const permalinkNode = post
          ? Array.from(post.querySelectorAll("a[href]")).find((node) => (
            facebookPermalink(node.href)
          ))
          : null;
        const dateLink = dateReference?.closest("a[href]")
          || permalinkNode
          || null;
        const permalink = facebookPermalink(
          permalinkNode?.href || dateLink?.href
        );
        const postId = facebookPostId(permalink);
        const date = facebookDateLabel(
          referencedLabel(dateLink),
          dateLink?.getAttribute("aria-label"),
          dateLink?.getAttribute("title"),
          renderedLeafText(dateLink)
        );
        return {
          display_name: displayName,
          friends_count_text: preferredFriendsCountText,
          friends_text: friendsText,
          followers_count_text: collapse(followersMatch?.[1], 200),
          bio: profileBio,
          details: profileDetails,
          external_links: detailLinks,
          profile_photo_url: profilePhotoUrl,
          profile_photo_identity: facebookPhotoIdentity(profilePhotoUrl),
          cover_photo_url: coverPhotoUrl,
          cover_photo_identity: facebookPhotoIdentity(coverPhotoUrl),
          loaded_post_count: postRoots.length,
          latest_post: {
            id: postId,
            date,
            content: collapse(messageRaw),
            content_truncated: messageRaw.length > request.maxItemLength,
            permalink,
            position: Number(post?.getAttribute("aria-posinset") || 0),
            pinned: Boolean(post && isPinned(post)),
          },
        };
      };
      for (const metric of request.metrics) {
        const selector = request.selectors[metric];
        if (selector) {
          customMetrics[metric] = selectorMetric(metric, selector);
        }
      }

      const allLinks = Array.from(document.querySelectorAll("a[href]"));
      const links = allLinks.slice(0, request.maxLinks).map((node) => ({
        href: collapse(node.href, 4000),
        text: collapse(node.textContent),
        aria_label: collapse(node.getAttribute("aria-label")),
      }));
      const labelNodes = Array.from(
        document.querySelectorAll("[aria-label], [title]")
      );
      const labeledTexts = [];
      const labelSeen = new Set();
      for (const node of labelNodes.slice(0, request.maxLabels)) {
        for (const value of [
          node.getAttribute("aria-label"),
          node.getAttribute("title"),
          node.textContent,
        ]) {
          const text = collapse(value);
          if (!text || labelSeen.has(text)) continue;
          labelSeen.add(text);
          labeledTexts.push(text);
          if (labeledTexts.length >= request.maxLabels) break;
        }
        if (labeledTexts.length >= request.maxLabels) break;
      }
      const jsonLd = Array.from(
        document.querySelectorAll('script[type="application/ld+json"]')
      )
        .slice(0, request.maxJsonLdItems)
        .map((node) => String(node.textContent || "").trim())
        .filter(Boolean)
        .map((value) => value.slice(0, request.maxJsonLdLength));
      const facebookProfile = facebookProfileSignals();

      const bodyRaw = String(document.body?.innerText || "");
      const bodyPreview = collapse(bodyRaw, 10000).toLocaleLowerCase();
      const href = String(location.href || "");
      let blockingReason = "";
      if (href.startsWith("chrome-error://")) {
        blockingReason = "navigation_error";
      } else if (
        document.querySelector('input[type="password"]')
        && /(?:login|log-in|signin|sign-in|auth)/i.test(href)
      ) {
        blockingReason = "authentication_required";
      } else if (
        /captcha|verify you are human|unusual traffic|security check|access denied/
          .test(bodyPreview)
      ) {
        blockingReason = "challenge_required";
      } else {
        const consentDialog = Array.from(
          document.querySelectorAll(
            'dialog, [role="dialog"], [aria-modal="true"]'
          )
        ).find((node) => {
          const style = getComputedStyle(node);
          const rect = node.getBoundingClientRect();
          if (
            style.display === "none"
            || style.visibility === "hidden"
            || rect.width <= 0
            || rect.height <= 0
          ) {
            return false;
          }
          const text = collapse(node.innerText, 5000).toLocaleLowerCase();
          return (
            /cookie|consent|privacy/.test(text)
            && /accept|agree|allow|continue/.test(text)
          );
        });
        if (consentDialog) blockingReason = "consent_required";
      }

      return {
        final_url: href,
        metadata: {
          ready_state: String(document.readyState || ""),
          language: collapse(document.documentElement?.lang, 100),
          canonical_url: collapse(
            document.querySelector('link[rel~="canonical" i]')?.href,
            4000
          ),
          content_type: collapse(document.contentType, 200),
          blocking_reason: blockingReason,
        },
        custom_metrics: customMetrics,
        signals: {
          title: collapse(document.title),
          meta_description: collapse(
            document.querySelector('meta[name="description" i]')?.content,
            20000
          ),
          og_title: collapse(
            document.querySelector('meta[property="og:title" i]')?.content
          ),
          og_description: collapse(
            document.querySelector(
              'meta[property="og:description" i]'
            )?.content,
            20000
          ),
          body_text: collapse(bodyRaw, request.maxBodyTextLength),
          body_text_truncated: bodyRaw.length > request.maxBodyTextLength,
          links,
          labeled_texts: labeledTexts,
          json_ld: jsonLd,
          facebook_profile: facebookProfile,
        },
        errors,
        diagnostics: {
          requested_metrics: request.metrics.length,
          custom_metrics: Object.keys(customMetrics).length,
          link_count: links.length,
          labeled_text_count: labeledTexts.length,
          json_ld_count: jsonLd.length,
          facebook_post_count: Number(
            facebookProfile.loaded_post_count || 0
          ),
        },
      };
    })()
    """.replace("__SYNTHESIX_SOCIAL_REQUEST__", request)
    observability.count("monitor_social_probe")
    result = await tab.evaluate(script)
    if not isinstance(result, Mapping):
        raise RuntimeError("Invalid social monitoring probe response.")
    return result
