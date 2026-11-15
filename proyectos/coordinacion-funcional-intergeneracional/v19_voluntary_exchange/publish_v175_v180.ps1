$ErrorActionPreference = 'Stop'
$taskProject = $PSScriptRoot
$taskRepo = (Resolve-Path (Join-Path $taskProject '..\..\..')).Path
$taskPrefix = 'proyectos/coordinacion-funcional-intergeneracional/v19_voluntary_exchange/'
$taskArchiveDir = Join-Path $taskProject 'research/V175_V180_20261115'
$taskExpectedRemote = '9404824721694a3d91c81dddb9f49aa46afd3284'
$taskBranch = 'research/aldea-memory-v175-20261115'
$taskRef = 'refs/heads/' + $taskBranch

function Invoke-TaskGit {
    $taskGitArguments = $args
    $taskOutput = & git -C $taskRepo @taskGitArguments
    if ($LASTEXITCODE -ne 0) { throw "Git failed: $($taskGitArguments[0])" }
    return $taskOutput
}

$taskCurrentHead = (Invoke-TaskGit rev-parse HEAD).Trim()
if ($taskCurrentHead -ne 'c032a32d2d8d7710a6ad5a88519b0801ea186891') { throw 'Local HEAD changed; inspect before publishing.' }
$taskLocalBranch = (Invoke-TaskGit branch --show-current).Trim()
$taskIndexOriginal = (Invoke-TaskGit rev-parse --git-path index).Trim()
if (-not [IO.Path]::IsPathRooted($taskIndexOriginal)) { $taskIndexOriginal = Join-Path $taskRepo $taskIndexOriginal }
$taskIndexOriginal = (Resolve-Path -LiteralPath $taskIndexOriginal).Path
$taskIndexShaBefore = (Get-FileHash -LiteralPath $taskIndexOriginal -Algorithm SHA256).Hash
$taskTemporaryIndex = Join-Path $taskArchiveDir 'git_publish_exact_bytes.index'
if (Test-Path -LiteralPath $taskTemporaryIndex) { throw 'Task index exists; inspect it rather than overwriting.' }
$taskReceiptPath = Join-Path $taskArchiveDir 'PUBLICATION_RECEIPT.json'
if (Test-Path -LiteralPath $taskReceiptPath) { throw 'A publication receipt already exists.' }
$taskArchiveReceipt = Get-Content -LiteralPath (Join-Path $taskArchiveDir 'PACKAGE_RECEIPT.json') -Raw | ConvertFrom-Json
$taskArchive = Join-Path $taskArchiveDir 'EVIDENCE.zip'
if ((Get-FileHash -LiteralPath $taskArchive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskArchiveReceipt.sha256) { throw 'Archive changed.' }
$taskRemoteBefore = ((Invoke-TaskGit ls-remote origin $taskRef) -split '\s+')[0]
if ($taskRemoteBefore -ne $taskExpectedRemote) { throw 'Remote branch advanced; inspect its new head before publishing.' }

$taskFiles = @(
 'research_resource_limits.py','v175_memory_evolution.py','v176_frozen_memory_causal.py',
 'v177_cognitive_gate_game.py','v178_private_affine_rival.py','v179_download_cpr_evidence.py',
 'v179_profile_cpr_archive.py','v179_replicate_waterway_effects.py','v180_open_policy_space.py',
 'close_v175_v180.py','v180_register_and_integrate.py','v180_verify_remote_prereg.py',
 'archive_v175_v180.py','publish_v175_v180.ps1','v180_verify_delivery.py','REPRODUCE_V175_V180.md','V175_REPRODUCTION.md',
 'PREREG_V175_LEARNED_ECOLOGICAL_MEMORY.md','PREREG_V176_FROZEN_MEMORY_CAUSAL.md',
 'PREREG_V177_COGNITIVE_GATE_GAME.md','PREREG_V178_PRIVATE_AFFINE_RIVAL.md','PREREG_V180_OPEN_POLICY_SPACE.md',
 'INICIO_INVESTIGACION_CIENTIFICA.md','handoff_codex/ESTADO_20261115_V180.md',
 'docs/TFM_MANUSCRITO_TRABAJO_V180.md','docs/TFM_CAPITULO_VALIDACION_AMPLIADA_V141_V150.md',
 'docs/TFM_CAPITULO_DISPONIBILIDAD_Y_ESTABILIDAD.md','docs/TFM_CAPITULO_MEMORIA_REPRESENTACION_Y_CONTRASTE_HUMANO.md',
 'literatura/references_verified.json','literatura/references.bib','literatura/BIBLIOGRAFIA_ACUMULATIVA_20261114.md',
 'results/INFORME_V175_V180_20261115.md','results/V175_V180_FINAL_AUDIT.json',
 'results/V175_V180_REVIEWED_STATISTICS.json','results/AB_EVALUACION_V175_V180_20261115.json','results/TFM_V180_BUILD.json',
 'results/V179_WATERWAY_DATA_PROFILE.json','results/V179_HUMAN_POINT_AND_RANDOMIZATION_REPLICATION.json',
 'results/FIG_V175_V180_CORE.png','results/FIG_V179_HUMAN_MONITORING.png','results/FIG_CT2_V175_V180.png',
 'results/v175_learned_memory/SUMMARY.json','results/v176_frozen_memory/SUMMARY.json','results/v177_gate_game/SUMMARY.json',
 'results/v178_private_affine_M5/SUMMARY.json','results/v180_open_policy_space/MAINTENANCE.json',
 'results/v180_open_policy_space/SELECTION.json','results/v180_open_policy_space/VALIDATION.json',
 'research/V175_V180_20261115/README.md','research/V175_V180_20261115/EVIDENCE.zip',
 'research/V175_V180_20261115/SHA256.json','research/V175_V180_20261115/PACKAGE_RECEIPT.json',
 'research/V175_V180_20261115/LEDGER_A_J.json','research/V175_V180_20261115/ENVIRONMENT.json',
 'research/V175_V180_20261115/requirements.txt','research/V175_V180_20261115/REMOTE_PREREG_BYTE_AUDIT.json',
 'research/V175_V180_20261115/GIT_STATE_BEFORE_PUBLICATION.json'
)

$taskPreviousIndexVariable = [Environment]::GetEnvironmentVariable('GIT_INDEX_FILE','Process')
try {
    $env:GIT_INDEX_FILE = $taskTemporaryIndex
    $null = Invoke-TaskGit read-tree $taskExpectedRemote
    foreach ($taskRelative in $taskFiles) {
        $taskAbsolute = Join-Path $taskProject $taskRelative
        if (-not (Test-Path -LiteralPath $taskAbsolute -PathType Leaf)) { throw "Missing payload: $taskRelative" }
        $taskBlob = (Invoke-TaskGit hash-object -w --no-filters -- $taskAbsolute).Trim()
        $taskRepoPath = $taskPrefix + $taskRelative
        $null = Invoke-TaskGit update-index --add --cacheinfo 100644 $taskBlob $taskRepoPath
    }
    $taskTree = (Invoke-TaskGit write-tree).Trim()
    $taskMessageFile = Join-Path $taskArchiveDir 'git_publish_message.txt'
    $taskMessage = @'
research: preserve exact V175–V180 bytes across Windows Git filters

Preserve 66 completed evolutions, frozen-policy causal audits and an independent
Python reconstruction of published human monitoring results. Retain failed
capacity, Pareto-trap, affine-rival, maintenance-collapse and invasion criteria.
Historical CT2 remains 61; no N2/N3 accreditation or external validation claim.

Retain the initial publication and correct text line-ending normalization.
Store exact blob bytes and an identical embedded/outer manifest. Scientific
results, preregistrations and manuscript claims are unchanged.
'@
    [IO.File]::WriteAllText($taskMessageFile,$taskMessage,[Text.UTF8Encoding]::new($false))
    $taskCommit = (Invoke-TaskGit commit-tree $taskTree -p $taskExpectedRemote -F $taskMessageFile).Trim()
    $null = Invoke-TaskGit merge-base --is-ancestor $taskExpectedRemote $taskCommit
    # Ordinary fast-forward push. A concurrent remote advance rejects this update.
    $null = Invoke-TaskGit -c pack.threads=2 push --porcelain origin ($taskCommit + ':' + $taskRef)
    $taskObserved = ((Invoke-TaskGit ls-remote origin $taskRef) -split '\s+')[0]
    if ($taskObserved -ne $taskCommit) { throw 'Remote head does not match the result commit.' }
} finally {
    if ($null -eq $taskPreviousIndexVariable) { Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue }
    else { $env:GIT_INDEX_FILE = $taskPreviousIndexVariable }
}

$taskIndexShaAfter = (Get-FileHash -LiteralPath $taskIndexOriginal -Algorithm SHA256).Hash
if ($taskIndexShaAfter -ne $taskIndexShaBefore) { throw 'Original index changed; preserve and investigate.' }
if ((Invoke-TaskGit rev-parse HEAD).Trim() -ne $taskCurrentHead) { throw 'Local HEAD changed.' }
if ((Invoke-TaskGit branch --show-current).Trim() -ne $taskLocalBranch) { throw 'Local branch changed.' }
$taskReceipt = [ordered]@{
 repository='GalexY3/Metodologia-AB';branch=$taskBranch;parent=$taskExpectedRemote;
 result_commit=$taskCommit;result_tree=$taskTree;remote_head_observed=$taskObserved;
 commit_url=('https://github.com/GalexY3/Metodologia-AB/commit/'+$taskCommit);
 archive_sha256=$taskArchiveReceipt.sha256;archive_bytes=$taskArchiveReceipt.bytes;
 exact_local_index_preserved=$true;original_index_sha256=$taskIndexShaBefore.ToLowerInvariant();
 local_head_preserved=$taskCurrentHead;local_branch_preserved=$taskLocalBranch;
 uploaded_paths=$taskFiles.Count;human_raw_ZIP_uploaded=$false;PR_created=$false;
 publication_helper='Git CLI streaming local binary; connector used for preregistration and post-publication verification';
 observed_utc=[DateTime]::UtcNow.ToString('o')
}
[IO.File]::WriteAllText($taskReceiptPath,($taskReceipt | ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
Write-Output ('PUBLISHED ' + $taskCommit + ' ; original index and HEAD preserved; archive ' + $taskArchiveReceipt.sha256)
