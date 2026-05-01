import os

file_path = r'c:\Users\hilar\BITACORA\bitacora\static\app.js'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

new_lines = []
skip = False
found_saveform = False

for i, line in enumerate(lines):
    if 'const oldSaveForm = saveForm;' in line:
        # Start of our clean saveForm
        new_lines.append(line)
        new_lines.append('saveForm = function(area) {\n')
        new_lines.append("  console.log('Iniciando saveForm para:', area);\n")
        new_lines.append('  try {\n')
        new_lines.append('    const err = validateArea(area);\n')
        new_lines.append("    const panel = document.getElementById('panel-' + area);\n")
        new_lines.append("    const actionRow = panel ? panel.querySelector('.action-row') : null;\n")
        new_lines.append('\n')
        new_lines.append('    if (err) {\n')
        new_lines.append("      console.warn('Error de validación:', err);\n")
        new_lines.append('      if (actionRow) {\n')
        new_lines.append('        const original = actionRow.innerHTML;\n')
        new_lines.append('        actionRow.innerHTML = `<div style="display:flex;align-items:center;gap:10px;color:var(--red-dark);font-weight:700;font-size:14px;">${err}</div>`;\n')
        new_lines.append('        setTimeout(() => { actionRow.innerHTML = original; }, 3500);\n')
        new_lines.append('      } else {\n')
        new_lines.append('        alert(err);\n')
        new_lines.append('      }\n')
        new_lines.append('      return;\n')
        new_lines.append('    }\n')
        new_lines.append('\n')
        new_lines.append('    const payload = {\n')
        new_lines.append("      id: 'REQ-' + Date.now().toString(36).toUpperCase() + '-' + Math.floor(Math.random()*1000),\n")
        new_lines.append('      area,\n')
        new_lines.append("      fecha: document.getElementById(area + '-fecha')?.value || '',\n")
        new_lines.append("      horaInicio: document.getElementById(area + '-hora')?.value || '',\n")
        new_lines.append("      horaFin: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true }).toLowerCase(),\n")
        new_lines.append("      maquina: document.getElementById(area + '-maquina')?.value || '',\n")
        new_lines.append("      mo: document.getElementById(area + '-mo')?.value || '',\n")
        new_lines.append("      item: document.getElementById(area + '-item')?.value || '',\n")
        new_lines.append("      descripcion: document.getElementById(area + '-desc')?.value || '',\n")
        new_lines.append('      turno: lastDetectedTurno || detectTurno(),\n')
        new_lines.append("      auditor: getSession()?.name || 'Sistema',\n")
        new_lines.append("      filas: document.getElementById(area + '-body')?.querySelectorAll('tr').length || 0,\n")
        new_lines.append('      guardadoAt: Date.now()\n')
        new_lines.append('    };\n')
        new_lines.append('\n')
        new_lines.append("    console.log('Guardando payload:', payload);\n")
        new_lines.append('    const saves = getSaves();\n')
        new_lines.append('    saves.push(payload);\n')
        new_lines.append('    localStorage.setItem(STORAGE_SAVES_KEY, JSON.stringify(saves));\n')
        new_lines.append('    \n')
        new_lines.append('    updateStats(); \n')
        new_lines.append("    if (typeof renderHistoryRecords === 'function') renderHistoryRecords();\n")
        new_lines.append('\n')
        new_lines.append("    const fDate = document.getElementById(area + '-fecha');\n")
        new_lines.append("    const fTime = document.getElementById(area + '-hora');\n")
        new_lines.append('    if (fDate) fDate._locked = true;\n')
        new_lines.append('    if (fTime) fTime._locked = true;\n')
        new_lines.append('\n')
        new_lines.append('    if (actionRow) {\n')
        new_lines.append('      const original = actionRow.innerHTML;\n')
        new_lines.append('      actionRow.innerHTML = `<div style="display:flex;align-items:center;gap:10px;color:var(--green);font-weight:700;font-size:14px;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Registro guardado correctamente.</div>`;\n')
        new_lines.append('      setTimeout(() => { actionRow.innerHTML = original; }, 3500);\n')
        new_lines.append('    }\n')
        new_lines.append('\n')
        new_lines.append('    clearAreaData(area);\n')
        new_lines.append("    console.log('Formulario guardado y limpiado.');\n")
        new_lines.append('\n')
        new_lines.append('  } catch (e) {\n')
        new_lines.append("    console.error('Error en saveForm:', e);\n")
        new_lines.append("    alert('Error al guardar: ' + e.message);\n")
        new_lines.append('  }\n')
        new_lines.append('};\n')
        
        # Now SKIP everything until the next block we recognize
        skip = True
        found_saveform = True
        continue
    
    if skip:
        # Stop skipping when we hit the next stable part of the file
        if 'const oldInitApp = initApp;' in line:
            skip = False
            new_lines.append('\n') # add a spacer
            new_lines.append(line)
        continue
    
    if not skip:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

if found_saveform:
    print("Successfully cleaned up saveForm and removed duplications.")
else:
    print("Could not find the target code to clean up.")
