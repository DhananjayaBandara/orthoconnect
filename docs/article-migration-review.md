# Article migration review

## Scope and outcome

This local, noindex draft preview contains **exactly the 40 supplied archive entries (19 English, 21 Sinhala)**. The five earlier dummy articles have been removed from the catalog, source files, generated pages, home previews and related links. The Sinhala children’s overview is one of the 40 entries, presented as a topic guide with its complete source material retained beneath the guide links. It is not counted twice.

The archive was read only. The importer checked ALL-ARTICLES.md against the individual-file manifest and used the individual UTF-8 Markdown files as the text authority. `content/article-migration.json` records source checksums, exact omitted blocks, outcomes and the retired article IDs. `content/article-assets.json` records the local image checksums and original image URLs. The normal build uses editable article JSON; it never re-imports the archive.

## Decisions requiring editorial review

1. **Overlapping English child articles:** en-children-01 and en-children-03 share 14 substantial paragraphs, including the humerus and supracondylar sections. Both remain separate drafts. The upper-arm article also contains additional material and repeated numbered complication lists. Choose the eventual article boundaries and reconcile the unique content before merging or retiring a route.
2. **Sinhala child guide:** si-overview-01 now links to all 11 individual Sinhala child topics. Its original text, headings and images remain in their original order below the new navigation. Compare the versions before consolidating: the overview includes material absent or worded differently in the individual articles. Some source headings and images appear mismatched (for example, trigger-finger and wrist diagrams alongside child dislocation topics). They are preserved for review rather than silently substituted.
3. **Clinical accuracy:** all imports remain drafts, with no author, reviewer or review date assigned. Review absolute treatment statements, exact recovery/operation timings, comparative claims about alternative treatment, statistical claims and outdated wording. The adult hip and foot/ankle sources contain shoulder/arm wording that appears copied from another topic. It has been preserved and requires correction by the clinician.
4. **Attribution and images:** the archive describes a different legacy practice. Do not infer authorship or offered services for the new doctor. First-person source passages and branded X-rays remain in the full local articles, with a draft notice. Source URLs are retained only in internal migration/provenance records; the website does not display an original-article link or direct readers to the archive website. Confirm attribution, image reuse and clinical relevance before release; do not erase watermarks or transfer legacy credentials.
5. **Language and classification:** native Sinhala titles and substantive copy are preserved. New summaries, controls and taxonomy labels need a Sinhala editorial check. The complex-fracture article is tagged for both adults and children because its source explicitly discusses both; audience-filter counts therefore overlap.
## Complete archive inventory

| Source ID | Article | Language | Audience | Body region | Topic | Original URL | Destination | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| en-adult-01 | Shoulder – Adults | en | Adults | Shoulder | Fractures & injuries, Joint dislocations | [Source](https://orthopaedic.lk/shoulder-adults/) | [Preview](../articles/en-adult-shoulder.html) | Separate draft |
| en-adult-02 | Upper Arm – Adults | en | Adults | Upper arm, Shoulder, Elbow | Fractures & injuries | [Source](https://orthopaedic.lk/upper-arm-adults/) | [Preview](../articles/en-adult-upper-arm.html) | Separate draft |
| en-adult-03 | Elbow – Adults | en | Adults | Elbow | Joint dislocations, Fractures & injuries | [Source](https://orthopaedic.lk/elbow-adults/) | [Preview](../articles/en-adult-elbow.html) | Separate draft |
| en-adult-04 | Forearm – Adults | en | Adults | Forearm, Elbow | Fractures & injuries | [Source](https://orthopaedic.lk/forearm-adults/) | [Preview](../articles/en-adult-forearm.html) | Separate draft |
| en-adult-05 | Wrist – Adults | en | Adults | Wrist & hand, Forearm | Fractures & injuries | [Source](https://orthopaedic.lk/wrist-adults/) | [Preview](../articles/en-adult-wrist.html) | Separate draft |
| en-adult-06 | Hip – Adults | en | Adults | Hip | Fractures & injuries | [Source](https://orthopaedic.lk/hip-adults/) | [Preview](../articles/en-adult-hip.html) | Separate draft |
| en-adult-07 | Thigh – Adults | en | Adults | Thigh, Knee | Fractures & injuries | [Source](https://orthopaedic.lk/thigh-adults/) | [Preview](../articles/en-adult-thigh.html) | Separate draft |
| en-adult-08 | Knee – Adults | en | Adults | Knee | Joint dislocations, Fractures & injuries | [Source](https://orthopaedic.lk/knee-adults/) | [Preview](../articles/en-adult-knee.html) | Separate draft |
| en-adult-09 | Leg – Adults | en | Adults | Lower leg, Knee | Fractures & injuries | [Source](https://orthopaedic.lk/leg-adults/) | [Preview](../articles/en-adult-leg.html) | Separate draft |
| en-adult-10 | Foot & Ankle – Adults | en | Adults | Foot & ankle | Fractures & injuries, Foot & ankle surgery | [Source](https://orthopaedic.lk/foot-ankle-adults/) | [Preview](../articles/en-adult-foot-ankle.html) | Separate draft |
| en-adult-11 | Pelvis – Adults | en | Adults | Pelvis | Fractures & injuries | [Source](https://orthopaedic.lk/pelvis-adults/) | [Preview](../articles/en-adult-pelvis.html) | Separate draft |
| en-adult-12 | Spine – Adults | en | Adults | Spine & back, Neck | Fractures & injuries | [Source](https://orthopaedic.lk/spine-adults/) | [Preview](../articles/en-adult-spine.html) | Separate draft |
| en-children-01 | Shoulder – Children | en | Children | Shoulder, Upper arm, Elbow | Fractures & injuries | [Source](https://orthopaedic.lk/shoulder-children/) | [Preview](../articles/en-children-shoulder.html) | Separate draft; overlap pending review |
| en-children-02 | Elbow – Children | en | Children | Elbow | Fractures & injuries | [Source](https://orthopaedic.lk/elbow-children/) | [Preview](../articles/en-children-elbow.html) | Separate draft |
| en-children-03 | Upper Arm – Children | en | Children | Upper arm, Shoulder, Elbow | Fractures & injuries | [Source](https://orthopaedic.lk/upper-arm-children/) | [Preview](../articles/en-children-upper-arm.html) | Separate draft; overlap pending review |
| en-children-04 | Wrist & Hand – Children | en | Children | Wrist & hand, Forearm | Fractures & injuries | [Source](https://orthopaedic.lk/wrist-hand-children/) | [Preview](../articles/en-children-wrist-hand.html) | Separate draft |
| en-children-05 | Knee – Children | en | Children | Knee | Joint dislocations | [Source](https://orthopaedic.lk/knee-children/) | [Preview](../articles/en-children-knee.html) | Separate draft |
| en-children-06 | Foot & Ankle – Children | en | Children | Foot & ankle | Fractures & injuries | [Source](https://orthopaedic.lk/foot-ankle-children/) | [Preview](../articles/en-children-foot-ankle.html) | Separate draft |
| en-children-07 | Leg – Children | en | Children | Lower leg | Fractures & injuries | [Source](https://orthopaedic.lk/leg-children/) | [Preview](../articles/en-children-leg.html) | Separate draft |
| si-adult-01 | අස්ථි බිදීම් | si | Adults | Shoulder, Upper arm, Elbow, Forearm, Wrist & hand, Hip, Thigh, Knee, Lower leg, Foot & ankle | Fractures & injuries | [Source](https://orthopaedic.lk/අස්ථි-බිදීම්/) | [Preview](../articles/si-adult-fractures.html) | Separate draft |
| si-adult-02 | උකුල සන්දිය දැමීම | si | Adults | Hip | Joint replacement | [Source](https://orthopaedic.lk/උකුල-සන්දිය-දැමීම/) | [Preview](../articles/si-adult-hip-replacement.html) | Separate draft |
| si-adult-03 | දණහිස සන්දිය දැමීම | si | Adults | Knee | Joint replacement | [Source](https://orthopaedic.lk/දණහිස-සන්දිය-දැමීම/) | [Preview](../articles/si-adult-knee-replacement.html) | Separate draft |
| si-adult-04 | සුලබව දක්නට ලැබෙන වේදනාවන් | si | Adults | Neck, Shoulder, Elbow, Wrist & hand, Spine & back, Foot & ankle | Pain & nerve problems | [Source](https://orthopaedic.lk/සුලබව-දක්නට-ලැබෙන-ඇඟපතේ-ව/) | [Preview](../articles/si-adult-common-pains.html) | Separate draft |
| si-adult-05 | සංකීර්ණ වූ අස්ථි බිඳීම් වලට ප්‍රතිකාර | si | Adults, Children | Lower leg, Thigh, Bones & joints generally | Fractures & injuries, Deformity & fracture healing | [Source](https://orthopaedic.lk/සංකීර්ණ-වූ-අස්ථි-බිඳීම්-ව/) | [Preview](../articles/si-adult-complex-fractures.html) | Separate draft |
| si-adult-06 | පාදය හා වළලුකර ආශ්‍රිත ශල්‍ය කර්ම | si | Adults | Foot & ankle | Foot & ankle surgery, Pain & nerve problems | [Source](https://orthopaedic.lk/පාදය-හා-වළලුකර-ආශ්‍රිත-කො/) | [Preview](../articles/si-adult-foot-ankle-surgery.html) | Separate draft |
| si-adult-07 | ඇද කුද කෙලින් කිරීම | si | Adults | Shoulder, Upper arm, Elbow, Forearm, Wrist & hand, Hip, Thigh, Knee, Lower leg, Foot & ankle | Deformity & fracture healing | [Source](https://orthopaedic.lk/ඇද-කුද-කෙලින්-කිරීම/) | [Preview](../articles/si-adult-deformity-correction.html) | Separate draft |
| si-adult-08 | සුව නොවූ අස්ථි බිඳීම් | si | Adults | Bones & joints generally | Fractures & injuries, Deformity & fracture healing | [Source](https://orthopaedic.lk/සුව-නොවූ-අස්ථි-බිඳීම්/) | [Preview](../articles/si-adult-unhealed-fractures.html) | Separate draft |
| si-adult-09 | ඔස්ටියෝපොරෝසිස් | si | Adults | Bones & joints generally, Spine & back, Hip, Wrist & hand, Shoulder | Bone health & osteoporosis, Fractures & injuries | [Source](https://orthopaedic.lk/e0-b6-94-e0-b7-83-e0-b7-8a-e0-b6-a7-e0-b7-92-e0-b6-ba-e0-b7-9d-e0-b6-b4-e0-b7-9c-e0-b6-bb-e0-b7-9d-e0-b7-83-e0-b7-92-e0-b7-83-e0-b7-8a/) | [Preview](../articles/si-adult-osteoporosis.html) | Separate draft |
| si-children-01 | ළදරුවන්ගේ ගැටළු | si | Children | Foot & ankle, Wrist & hand | Growth, development & walking, Deformity & fracture healing | [Source](https://orthopaedic.lk/වයස-අවුරුද්ද-දක්වා-ළදරුව/) | [Preview](../articles/si-children-infant-problems.html) | Separate draft |
| si-children-02 | අස්ථි බිඳීම් (ළමා) | si | Children | Shoulder, Upper arm, Elbow, Forearm, Wrist & hand, Hip, Thigh, Knee, Lower leg, Foot & ankle | Fractures & injuries | [Source](https://orthopaedic.lk/අස්ථි-බිඳීම්/) | [Preview](../articles/si-children-fractures.html) | Separate draft |
| si-children-03 | සන්ධි පැනීම් (ළමා) | si | Children | Bones & joints generally | Joint dislocations | [Source](https://orthopaedic.lk/සන්ධි-පැනීම්/) | [Preview](../articles/si-children-dislocations.html) | Separate draft |
| si-children-04 | කකුල් වල ඇද කුද (ළමා) | si | Children | Lower leg, Knee, Hip, Foot & ankle | Growth, development & walking, Deformity & fracture healing | [Source](https://orthopaedic.lk/කකුල්-වල-ඇද-කුද/) | [Preview](../articles/si-children-leg-deformities.html) | Separate draft |
| si-children-05 | දරුවන්ගේ ඇවිදීමේ අසාමාන්යතා (ළමා) | si | Children | Hip, Lower leg, Foot & ankle | Growth, development & walking | [Source](https://orthopaedic.lk/දරුවන්ගේ-ඇවිදීමේ-අසාමාන්/) | [Preview](../articles/si-children-walking-problems.html) | Separate draft |
| si-children-06 | අස්ථි තුළින් හටගන්නා ගෙඩි (ළමා) | si | Children | Bones & joints generally | Bone tumours | [Source](https://orthopaedic.lk/අස්ථි-තුළින්-හටගන්නා-ගෙඩ/) | [Preview](../articles/si-children-bone-tumours.html) | Separate draft |
| si-children-07 | අස්ථි හා සන්ධිවල සිදුවන ආසාදන (ළමා) | si | Children | Bones & joints generally | Bone & joint infections | [Source](https://orthopaedic.lk/අස්ථි-හා-සන්ධිවල-සිදුවන-ආ/) | [Preview](../articles/si-children-infections.html) | Separate draft |
| si-children-08 | කොන්දුනරටියේ ඇද වීම් (ළමා) | si | Children | Spine & back | Growth, development & walking, Deformity & fracture healing | [Source](https://orthopaedic.lk/කොන්දුනරටියේ-ඇද-වීම්/) | [Preview](../articles/si-children-spinal-deformities.html) | Separate draft |
| si-children-09 | වේදනාවන් (ළමා) | si | Children | Bones & joints generally, Knee, Lower leg | Pain & nerve problems | [Source](https://orthopaedic.lk/වේදනාවන්/) | [Preview](../articles/si-children-pains.html) | Separate draft |
| si-children-10 | දිඟු කාලීනව පවතින අන්ගවිල්කලතාවයන් (ළමා) | si | Children | Bones & joints generally | Deformity & fracture healing, Growth, development & walking | [Source](https://orthopaedic.lk/දිඟු-කාලීනව-පවතින-අන්ගවි/) | [Preview](../articles/si-children-longstanding-deformities.html) | Separate draft |
| si-children-11 | ගොඩ වෙදකමින් අතරමං වූ ඔබේ දරුවට (ළමා) | si | Children | Bones & joints generally | Problems after previous treatment, Fractures & injuries | [Source](https://orthopaedic.lk/ගොඩ-වෙදකමින්-අතරමං-වූ-ඔබේ/) | [Preview](../articles/si-children-previous-treatment.html) | Separate draft |
| si-overview-01 | ළමා පිටුව | si | Children | Shoulder, Upper arm, Elbow, Forearm, Wrist & hand, Hip, Thigh, Knee, Lower leg, Foot & ankle, Spine & back, Bones & joints generally | Growth, development & walking, Fractures & injuries, Joint dislocations, Deformity & fracture healing, Pain & nerve problems, Bone tumours, Bone & joint infections, Problems after previous treatment | [Source](https://orthopaedic.lk/ළමා-පිටුව/) | [Preview](../articles/si-children-overview.html) | Topic guide + complete source retained |

## Removed dummy articles

The following prototype articles were removed at the user’s request. Their source JSON and generated HTML files are deleted; these are retirement records, not live links:

- `fracture-surgery-questions`
- `hip-replacement-expectations`
- `knee-pain-assessment`
- `knee-replacement-questions`
- `ligament-injury-questions`

The import command creates only the 40 supplied articles. The normal build also removes stale HTML files for these explicitly retired IDs. Related-reading references point to supplied articles where there is a matching subject; other dummy references are removed.

## Article metadata

The children’s guide uses the Sinhala display title `ළමා පිටුව`. Its original mixed-language archive title remains in the article’s `archive.original_title` provenance field. No source-body text is omitted by this display-title change.

## Removal and formatting log

Exact omitted text is recorded in `content/article-migration.json`; the originals remain in the unchanged archive. No substantive clinical paragraph or source image was removed.

| Source ID | Reason | Removed text or formatting change |
| --- | --- | --- |
| en-adult-01 | placeholder | On the other hand we denounce with righteous indignation and dislike men who are so beguiled and demoralized by the charms of pleasure of the moment so blinded by desire that they cannot foresee. Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore  et dolore magna aliqua. |
| en-adult-01 | placeholder | On the other hand we denounce with righteous indignation and dislike men who are so beguiled and demoralized by the charms of pleasure of the moment so blinded by desire that they cannot foresee. Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore  et dolore magna aliqua. |
| en-adult-02 | placeholder | On the other hand we denounce with righteous indignation and dislike men who are so beguiled and demoralized by the charms of pleasure of the moment so blinded by desire that they cannot foresee. Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore  et dolore magna aliqua. |
| en-adult-05 | legacy-enquiry-prompt | My Problem Is Not Listed |
| en-adult-05 | legacy-enquiry-prompt | Please send us your inquery |
| en-adult-06 | legacy-enquiry-prompt | My Problem Is Not Listed |
| en-adult-07 | legacy-enquiry-prompt | My Problem Is Not Listed |
| en-adult-07 | legacy-enquiry-prompt | Please send us your inquery |
| en-adult-07 | legacy-enquiry-prompt | My Problem Is Not Listed? |
| en-adult-07 | legacy-enquiry-prompt | Please contact us |
| en-adult-08 | legacy-enquiry-prompt | My Problem Is Not Listed ? |
| en-adult-08 | legacy-enquiry-prompt | Please contact us. |
| en-adult-10 | legacy-enquiry-prompt | My Problem Is Not Listed |
| en-adult-10 | legacy-enquiry-prompt | Please contact us |
| en-adult-11 | legacy-enquiry-prompt | My Problem Is Not Listed |
| en-adult-11 | legacy-enquiry-prompt | Please contact us |
| en-adult-12 | legacy-enquiry-prompt | My Problem Is Not Listed |
| en-children-01 | legacy-enquiry-prompt | Your Problem Is Not Listed ? |
| en-children-01 | legacy-enquiry-prompt | Please send us your problem. |
| en-children-01 | legacy-enquiry-prompt | My Problem Is Not Listed |
| en-children-01 | legacy-enquiry-prompt | Please contact us |
| en-children-02 | legacy-enquiry-prompt | Your Problem Is Not Listed ? |
| en-children-02 | legacy-enquiry-prompt | Please send us your problem. |
| en-children-03 | legacy-enquiry-prompt | Your Problem Is Not Listed ? |
| en-children-03 | legacy-enquiry-prompt | Please send us your problem. |
| en-children-03 | legacy-enquiry-prompt | My Problem Is Not Listed |
| en-children-03 | legacy-enquiry-prompt | Please contact us |
| en-children-04 | legacy-enquiry-prompt | Your Problem Is Not Listed ? |
| en-children-04 | legacy-enquiry-prompt | Please send us your problem. |
| si-adult-01 | gallery-formatting | Linked gallery retained as local inline figures, in source order. |
| si-adult-09 | formatting-separator | --- |

Logged changes: {'placeholder': 3, 'legacy-enquiry-prompt': 26, 'gallery-formatting': 1, 'formatting-separator': 1}. Archive headings starting at H3 are promoted to H2 where necessary; text and order are unchanged. Original list numbering is retained. Image-only gallery bullets become local figures, with provenance retained.

## Images

The 390 original image placements resolve to 251 distinct byte-identical assets. Each is copied once under `assets/images/articles/` and retains its original bytes. Image descriptions were checked against contact sheets. Their English alternative text carries `lang="en"`, including inside Sinhala pages. Inline figures preserve their full aspect ratios; no image is cropped, retouched or rebranded.

## Build and verification

Run from the website folder:

```sh
python3 -B scripts/build_site.py
python3 -B scripts/check_site.py
python3 -B scripts/check_article_migration.py
```

Open `articles.html` directly, or serve this directory with `python3 -m http.server 8080 --bind 127.0.0.1` and open `http://127.0.0.1:8080/articles.html`.

Filter state is carried in shareable query parameters (`lang`, `audience`, `region`, `topic`, `q`). Article links carry the originating query in `library`; breadcrumbs and return links restore that query without cookies or browser storage. Direct Sinhala reading links return to the Sinhala collection by default.

Validation results and environment limits are recorded in `docs/article-validation.md`. No publication or deployment was performed.

## Maintenance

Edit `content/articles/<id>.json`, then rebuild. The importer is a separate migration tool: it refuses to overwrite existing imports unless `--replace` is explicitly provided. A deliberate re-import regenerates imported drafts and this report, so preserve editorial changes before using that option.
