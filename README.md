# Tommaso Guarnaccia — personal portfolio

The portfolio is static HTML with a Git-based editor. GitHub owns deployment and
the repository owner controls the files. The website has no payment system,
advertising, analytics, or mailing-list services.

## Publish from GitHub

Use a repository in your own account. For a root GitHub Pages address, name it
`YOUR-USERNAME.github.io`. On GitHub Free the repository is public, so add only
material already approved for public release. Keep the default branch named
`main`. Under Settings → Pages, select GitHub Actions. In Actions → Publish
portfolio, run the workflow for the initial deployment. Later edits to main
trigger a rebuild and deployment automatically. The workflow generates canonical
URLs and the sitemap from the current GitHub Pages address.

## Write and edit in your browser

1. Open [Pages CMS](https://app.pagescms.org) and sign in with GitHub.
2. Install the GitHub app for this repository and select the main branch. You
   can limit the app to this repository in GitHub.
3. Open **Articles and other entries** and select **New**. Choose the section,
   set the publication date and summary, and write or paste into the visual editor.
4. Select **Include in The American Mind project** to also surface an essay,
   research or reading note, or video on that project page. Supply an HTTPS
   destination for a video.
5. Save once the entry is ready to go public. To revise it, open the same entry
   and save the changes. Keep unpublished drafts outside the public repository.
6. Check **Actions → Publish portfolio** on GitHub for deployment progress.

Use **Profile and education** to update your introduction, contact details,
education and headshot. Use **The American Mind project** to revise the project
description, questions and references. When updating your CV, replace
`assets/Tommaso_Guarnaccia_CV.pdf` in GitHub with your revised PDF at the same
path. To keep a backup, use GitHub’s **Code → Download ZIP**.

## Connect a domain

Register it in your own registrar account. Verify the domain in GitHub, add
it in the repository’s Pages settings, and use the DNS records in GitHub’s
[custom domain instructions](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).
Enable Enforce HTTPS once GitHub finishes the certificate. Run **Publish
portfolio** again so the site uses the final canonical address in metadata.

## Preview and portability

Python 3.10+ and Pandoc build the source. No server or runtime packages are
required once built.

```sh
python3 build.py --preview
python3 -m http.server --directory dist
```

The Capitol artwork is an AI-generated editorial illustration.
